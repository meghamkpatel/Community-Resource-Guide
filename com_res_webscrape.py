import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="huggingface_hub")

from bs4 import BeautifulSoup, FeatureNotFound
import requests
import io
import json
import hashlib
import time
import concurrent.futures
import threading
import os
import glob
import random
import re
import chardet
from google.api_core.exceptions import ServiceUnavailable
from requests.exceptions import ConnectionError, HTTPError
from google.cloud import storage
from google.oauth2 import service_account
from PyPDF2 import PdfReader
from urllib.parse import urljoin, urlparse
from sentence_transformers import SentenceTransformer

class ComResGuideWebScanner:
    def __init__(self, base_url, bucket_name, credentials_path, embedding_model_name='all-MiniLM-L6-v2', max_urls_to_visit=300, chunk_size=2048, rate_limit=10, time_window=60):
        self.visited_urls = set()
        self.urls_to_visit = set([base_url])
        self.base_url = base_url
        self.max_urls_to_visit = max_urls_to_visit
        self.bucket_name = bucket_name
        self.chunk_size = chunk_size

        # Rate limiting parameters
        self.rate_limit = rate_limit
        self.time_window = time_window
        self.requests_made = 0
        self.start_time = time.time()
        self.lock = threading.Lock()

        # Load credentials from the JSON key file
        self.credentials = service_account.Credentials.from_service_account_file(credentials_path)
        self.storage_client = storage.Client(credentials=self.credentials)
        self.bucket = self.storage_client.bucket(bucket_name)

        # Initialize Sentence-Transformers model
        self.embedding_model = SentenceTransformer(embedding_model_name)

        # Domains to skip
        self.skip_domains = ["guidestar.org", "propublica.org", "causeiq.com", "charitynavigator.org", "facebook.com"]

        # Headers to mimic a regular browser
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def fetch_content(self, url):
        with self.lock:
            current_time = time.time()
            elapsed_time = current_time - self.start_time

            if elapsed_time > self.time_window:
                self.start_time = current_time
                self.requests_made = 0

            if self.requests_made >= self.rate_limit:
                sleep_time = self.time_window - elapsed_time + random.uniform(0, 5)
                print(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
                self.start_time = time.time()
                self.requests_made = 0

            self.requests_made += 1

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.content
        except HTTPError as e:
            if e.response.status_code == 403:
                print(f"403 Forbidden error for URL: {url}")
            else:
                print(f"HTTP error: {e}")
            return None
        except requests.RequestException as e:
            print(f"Error fetching URL: {e}")
            return None

    def parse_pdf(self, pdf_content):
        try:
            pdf_reader = PdfReader(io.BytesIO(pdf_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return None

    def parse_web_page(self, content, url):
        if content and url not in self.visited_urls:
            detected = chardet.detect(content)
            encoding = detected['encoding'] if detected['encoding'] is not None else 'utf-8'
            html_content = content.decode(encoding, errors='replace')

            # Determine if the content is XML or HTML
            soup = None
            if html_content.strip().startswith('<?xml'):
                try:
                    soup = BeautifulSoup(html_content, 'xml')
                except Exception as e:
                    print(f"Error parsing XML: {e}")
            else:
                for parser in ["html.parser", "lxml", "html5lib"]:
                    try:
                        soup = BeautifulSoup(html_content, parser)
                        break
                    except FeatureNotFound:
                        continue
                    except Exception as e:
                        print(f"Error parsing with {parser}: {e}")
                        continue

            if soup is None:
                print(f"Could not parse content for URL: {url}")
                return [], '', None

            # Extract meta information
            meta_info = [meta.attrs for meta in soup.find_all('meta')]

            # Extract body text
            body_text = soup.get_text(separator='\n', strip=True)

            # Clean up the body text
            cleaned_body_text = self.clean_text(body_text)

            # Add the URL to the visited set
            self.visited_urls.add(url)

            return meta_info, cleaned_body_text, soup
        else:
            return [], '', None

    def clean_text(self, text):
        # Remove HTML tags
        clean_text = re.sub(r'<.*?>', '', text)
        # Normalize whitespace
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        # Handle special characters
        clean_text = clean_text.replace('\ufffd', ' ')
        return clean_text

    def get_blob_name(self, url, index=0):
        # Generate a hash for the URL to use as a unique identifier
        return f"{hashlib.md5(url.encode()).hexdigest()}_{index}.json"

    def save_text_and_embeddings_to_gcs(self, meta_info, body_text, url):
        is_rfp = self.check_for_rfp(body_text)
        chunks = [body_text[i:i + self.chunk_size] for i in range(0, len(body_text), self.chunk_size)]
        for index, chunk in enumerate(chunks):
            # Generate embeddings using Sentence-Transformers model
            embeddings = self.get_embeddings(chunk)

            data = {
                "url": url,
                "meta_info": meta_info,
                "body_text": chunk,
                "embeddings": embeddings,
                "is_rfp": is_rfp
            }
            blob_name = self.get_blob_name(url, index)
            blob = self.bucket.blob(blob_name)

            # Retry logic for uploading to GCS
            max_retries = 5
            for attempt in range(max_retries):
                try:
                    blob.upload_from_string(data=json.dumps(data), content_type='application/json')
                    break
                except (ServiceUnavailable, ConnectionError) as e:
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        print(f"Service unavailable or connection error. Retrying in {wait_time:.2f} seconds...")
                        time.sleep(wait_time)
                    else:
                        print(f"Failed to upload blob {blob_name} after {max_retries} attempts.")
                        raise

    def check_for_rfp(self, text):
        return 'request for proposal' in text.lower() or 'rfp' in text.lower()

    def get_embeddings(self, text):
        try:
            embeddings = self.embedding_model.encode(text)
            return embeddings.tolist()  # Convert to list for JSON serialization
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return []

    def is_valid_url(self, url):
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        if any(skip_domain in domain for skip_domain in self.skip_domains):
            print(f"Skipping URL with domain: {domain}")
            return False
        return bool(parsed_url.scheme) and bool(parsed_url.netloc) and urlparse(self.base_url).netloc in urlparse(url).netloc

    def process_url(self, url):
        content = self.fetch_content(url)
        if content:
            parsed_url = urlparse(url)
            if parsed_url.path.endswith(".pdf"):
                body_text = self.parse_pdf(content)
                if body_text is not None:
                    meta_info = [{'name': 'title', 'content': os.path.basename(parsed_url.path)}]
                    self.save_text_and_embeddings_to_gcs(meta_info, body_text, url)
            else:
                meta_info, body_text, soup = self.parse_web_page(content, url)
                if soup:
                    self.save_text_and_embeddings_to_gcs(meta_info, body_text, url)
                    # Extract URLs from the current page and add them to the list of URLs to visit
                    urls = [urljoin(url, link.get('href')) for link in soup.find_all('a', href=True)]
                    for new_url in urls:
                        if self.is_valid_url(new_url) and new_url not in self.visited_urls and new_url not in self.urls_to_visit:
                            self.urls_to_visit.add(new_url)
        return None

    def start_scanning(self):
        while self.urls_to_visit and len(self.visited_urls) < self.max_urls_to_visit:
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                future_to_url = {executor.submit(self.process_url, url): url for url in self.urls_to_visit}
                self.urls_to_visit = set()
                for future in concurrent.futures.as_completed(future_to_url):
                    future.result()

def main():
    bucket_name = 'community_resource_nc'
    folder_path = r"C:\Users\Megha Patel\Documents\com docs"  # Path to the folder containing JSON files with websites
    credentials_path = r"C:\Users\Megha Patel\Downloads\community-resource-guide-3002b8ea07bb.json"  # Path to your service account JSON file

    # Get list of JSON files in the folder
    json_files = glob.glob(os.path.join(folder_path, '*.json'))

    for json_file in json_files:
        print(f"Processing file: {json_file}")
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

            for entry in data:
                organization_name = entry.get("Organization Name")
                zipcode = entry.get("Zipcode")
                websites = entry.get("websites", {})
                website = websites.get(organization_name)
                if not website or any(domain in website for domain in ["guidestar.org", "propublica.org", "causeiq.com", "charitynavigator.org", "facebook.com"]):
                    print(f"Skipping {organization_name} in zipcode {zipcode} due to invalid website: {website}")
                    continue

                print(f"Scanning website for {organization_name} in zipcode {zipcode}: {website}")
                scanner = ComResGuideWebScanner(website, bucket_name, credentials_path)
                scanner.start_scanning()

if __name__ == "__main__":
    main()
