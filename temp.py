import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from google.cloud import storage
from google.oauth2 import service_account
from PyPDF2 import PdfReader
import io
import json
import hashlib
import os
import time

class SinglePageExtractor:
    def __init__(self, url, bucket_name, credentials_path, chunk_size=2048):
        self.url = url
        self.bucket_name = bucket_name
        self.chunk_size = chunk_size
        
        # Load credentials from the JSON key file
        self.credentials = service_account.Credentials.from_service_account_file(credentials_path)
        self.storage_client = storage.Client(credentials=self.credentials)
        self.bucket = self.storage_client.bucket(bucket_name)

    def fetch_content(self):
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            print(f"Error fetching URL: {e}")
            return None

    def parse_pdf(self, pdf_content):
        pdf_reader = PdfReader(io.BytesIO(pdf_content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text

    def parse_web_page(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract meta information
        meta_info = [meta.attrs for meta in soup.find_all('meta')]

        # Extract body text
        body_text = soup.get_text(separator='\n', strip=True)

        return meta_info, body_text

    def get_blob_name(self, index=0):
        # Generate a hash for the URL to use as a unique identifier
        return f"{hashlib.md5(self.url.encode()).hexdigest()}_{index}.json"

    def save_text_to_gcs(self, meta_info, body_text):
        chunks = [body_text[i:i + self.chunk_size] for i in range(0, len(body_text), self.chunk_size)]
        for index, chunk in enumerate(chunks):
            data = {
                "url": self.url,
                "meta_info": meta_info,
                "body_text": chunk
            }
            blob_name = self.get_blob_name(index)
            blob = self.bucket.blob(blob_name)
            
            # Check if the blob already exists
            if blob.exists():
                print(f"Blob {blob_name} already exists. Overwriting.")
            else:
                print(f"Saving new blob {blob_name}.")

            blob.upload_from_string(data=json.dumps(data), content_type='application/json')

    def process_url(self):
        content = self.fetch_content()
        if content:
            parsed_url = urlparse(self.url)
            if parsed_url.path.endswith(".pdf"):
                body_text = self.parse_pdf(content)
                meta_info = [{'name': 'title', 'content': os.path.basename(parsed_url.path)}]
            else:
                meta_info, body_text = self.parse_web_page(content)
            self.save_text_to_gcs(meta_info, body_text)

def main():
    bucket_name = 'durham-bot'
    url = 'https://www.madeindurham.org/welcome-from-the-chair'  # Example base URL
    credentials_path = r'C:\Users\Megha Patel\Downloads\community-resource-guide-3002b8ea07bb.json'  # Path to your service account JSON file
    extractor = SinglePageExtractor(url, bucket_name, credentials_path)
    extractor.process_url()

if __name__ == "__main__":
    main()
