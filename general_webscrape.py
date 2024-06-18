import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from google.cloud import storage
from google.oauth2 import service_account
from PyPDF2 import PdfReader
import io
import json
import hashlib
import time
import concurrent.futures
import threading
import os
import streamlit as st
from sentence_transformers import SentenceTransformer

class WebScanner:
    def __init__(self, base_url, bucket_name, credentials_path, max_urls_to_visit=300, chunk_size=2048, rate_limit=10, time_window=60, max_content_size=10*1024*1024):
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

        # Maximum content size to download
        self.max_content_size = max_content_size

        # Load credentials from the JSON key file
        self.credentials = service_account.Credentials.from_service_account_file(credentials_path)
        self.storage_client = storage.Client(credentials=self.credentials)
        self.bucket = self.storage_client.bucket(bucket_name)

        # Initialize the embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    def fetch_content(self, url):
        with self.lock:
            current_time = time.time()
            elapsed_time = current_time - self.start_time

            if elapsed_time > self.time_window:
                self.start_time = current_time
                self.requests_made = 0

            if self.requests_made >= self.rate_limit:
                sleep_time = self.time_window - elapsed_time
                print(f"Rate limit reached. Sleeping for {sleep_time} seconds...")
                time.sleep(sleep_time)
                self.start_time = time.time()
                self.requests_made = 0

            self.requests_made += 1

        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            content_size = int(response.headers.get('Content-Length', 0))
            if content_size > self.max_content_size:
                print(f"Content size {content_size} exceeds maximum limit. Skipping URL: {url}")
                return None

            content = response.content
            if len(content) > self.max_content_size:
                print(f"Content size {len(content)} exceeds maximum limit after download. Skipping URL: {url}")
                return None

            return content
        except requests.RequestException as e:
            print(f"Error fetching URL: {e}")
            return None

    def parse_pdf(self, pdf_content):
        pdf_reader = PdfReader(io.BytesIO(pdf_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text

    def parse_web_page(self, html_content, url):
        if html_content and url not in self.visited_urls:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract meta information
            meta_info = [meta.attrs for meta in soup.find_all('meta')]

            # Extract body text
            body_text = soup.get_text(separator='\n', strip=True)

            # Add the URL to the visited set
            self.visited_urls.add(url)

            return meta_info, body_text, soup
        else:
            return [], '', None

    def get_blob_name(self, url, index=0):
        # Generate a hash for the URL to use as a unique identifier
        return f"{hashlib.md5(url.encode()).hexdigest()}_{index}.json"

    def save_text_and_embeddings_to_gcs(self, meta_info, body_text, url):
        chunks = [body_text[i:i + self.chunk_size] for i in range(0, len(body_text), self.chunk_size)]
        for index, chunk in enumerate(chunks):
            # Generate a hash of the chunk
            chunk_hash = hashlib.md5(chunk.encode()).hexdigest()

            # Generate embeddings using the embedding model
            embeddings = self.get_embeddings(chunk)

            data = {
                "url": url,
                "meta_info": meta_info,
                "body_text": chunk,
                "embeddings": embeddings,
                "hash": chunk_hash
            }

            blob_name = self.get_blob_name(url, index)
            blob = self.bucket.blob(blob_name)

            if blob.exists():
                # Download existing blob
                existing_data = json.loads(blob.download_as_string())
                existing_hash = existing_data.get("hash", "")

                if existing_hash == chunk_hash:
                    print(f"Blob {blob_name} already exists with the same content. Skipping.")
                    continue
                else:
                    print(f"Blob {blob_name} exists but with different content. Updating.")
            else:
                print(f"Saving new blob {blob_name}.")

            blob.upload_from_string(data=json.dumps(data), content_type='application/json')

    def get_embeddings(self, text):
        try:
            embeddings = self.embedding_model.encode(text).tolist()
            return embeddings
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            return []

    def is_valid_url(self, url):
        parsed_url = urlparse(url)
        return bool(parsed_url.scheme) and bool(parsed_url.netloc) and urlparse(self.base_url).netloc in urlparse(url).netloc

    def process_url(self, url):
        content = self.fetch_content(url)
        if content:
            parsed_url = urlparse(url)
            if parsed_url.path.endswith(".pdf"):
                body_text = self.parse_pdf(content)
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
    bucket_name = 'bear_brown_co'
    base_url = 'https://bearbrown.co/'  # Example base URL
    credentials_path = r"C:\Users\Megha Patel\Downloads\community-resource-guide-3002b8ea07bb.json"  # Path to your service account JSON file
    scanner = WebScanner(base_url, bucket_name, credentials_path)
    scanner.start_scanning()

if __name__ == "__main__":
    main()
