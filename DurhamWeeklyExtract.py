import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from google.cloud import storage
from google.oauth2 import service_account
import json
import hashlib
import os
import time


class MadeInDurhamWebScanner:
    def __init__(self, base_url, bucket_name, credentials_path, max_urls_to_visit=300):
        self.visited_urls = set()
        self.base_url = base_url
        self.max_urls_to_visit = max_urls_to_visit
        self.bucket_name = bucket_name
        
        # Load credentials from the JSON key file
        self.credentials = service_account.Credentials.from_service_account_file(credentials_path)
        self.storage_client = storage.Client(credentials=self.credentials)
        self.bucket = self.storage_client.bucket(bucket_name)

    def fetch_web_page(self, url, retries=5):
        for attempt in range(retries):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                if response.status_code == 429:
                    print(f"Error fetching URL: {e}. Retrying in {2 ** attempt} seconds.")
                    time.sleep(2 ** attempt)
                else:
                    print(f"Error fetching URL: {e}")
                    return None
        return None

    def parse_web_page(self, html_content, url):
        if html_content and url not in self.visited_urls:
            self.visited_urls.add(url)
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract meta information
            meta_info = [meta.attrs for meta in soup.find_all('meta')]

            # Extract body text
            body_text = soup.get_text(separator='\n', strip=True)

            return meta_info, body_text
        else:
            return [], ''

    def get_blob_name(self, url):
        # Generate a hash for the URL to use as a unique identifier
        return hashlib.md5(url.encode()).hexdigest() + '.json'

    def save_text_to_gcs(self, meta_info, body_text, url):
        data = {
            "url": url,
            "meta_info": meta_info,
            "body_text": body_text
        }
        blob_name = self.get_blob_name(url)
        blob = self.bucket.blob(blob_name)

        # Check if the blob already exists
        if blob.exists():
            print(f"Blob {blob_name} already exists. Overwriting.")
        else:
            print(f"Saving new blob {blob_name}.")

        blob.upload_from_string(data=json.dumps(data), content_type='application/json')

    def is_valid_url(self, url):
        parsed_url = urlparse(url)
        return bool(parsed_url.scheme) and bool(parsed_url.netloc)

    def start_scanning(self):
        urls_to_visit = [self.base_url]
        while urls_to_visit and len(self.visited_urls) < self.max_urls_to_visit:
            url = urls_to_visit.pop(0)
            html_content = self.fetch_web_page(url)
            if html_content:
                meta_info, body_text = self.parse_web_page(html_content, url)
                self.save_text_to_gcs(meta_info, body_text, url)

                # Extract URLs from the current page and add them to the list of URLs to visit
                soup = BeautifulSoup(html_content, 'html.parser')
                urls = [urljoin(url, link.get('href')) for link in soup.find_all('a', href=True)]
                for new_url in urls:
                    if self.is_valid_url(new_url) and new_url not in self.visited_urls and new_url not in urls_to_visit:
                        urls_to_visit.append(new_url)

def main():
    bucket_name = 'durham-bot'
    base_url = 'https://www.madeindurham.org/'
    credentials_path = r'C:\Users\Megha Patel\Downloads\community-resource-guide-3002b8ea07bb.json'  # Path to your service account JSON file
    scanner = MadeInDurhamWebScanner(base_url, bucket_name, credentials_path)
    scanner.start_scanning()

    base_url = 'https://static1.squarespace.com/static/6234e702a606aa02305e7e4c/t/663906c6e6853e33536af6d1/1715013319412/BULLS23-C9-RECRUIT-Info-Flyer-0416.pdf'
    credentials_path = r'C:\Users\Megha Patel\Downloads\community-resource-guide-3002b8ea07bb.json'  # Path to your service account JSON file
    scanner = MadeInDurhamWebScanner(base_url, bucket_name, credentials_path)
    scanner.start_scanning()

if __name__ == "__main__":
    main()
