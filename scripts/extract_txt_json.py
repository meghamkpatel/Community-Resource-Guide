import urllib.request
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.error import HTTPError
import json
import os
import numpy as np
import scipy
import requests
import time

class PMTWebScannerSpider:
    def __init__(self):
        self.visited_urls = set()
        self.base_url = None  # Base URL for beauty products
        self.max_urls_to_visit = 300  # Maximum number of URLs to visit

        # Create a session object to persist cookies across requests
        self.session = requests.Session()

    def fetch_web_page(self, url):
        try:
            response = self.session.get(url, verify=False, timeout=10)  # Timeout set to 10 seconds
            return response.text
        except Exception as e:
            print(f"Error fetching URL: {e}")
            return None

    def parse_web_page(self, html_content, url):
        if html_content is not None and url not in self.visited_urls:
            self.visited_urls.add(url)
            soup = BeautifulSoup(html_content, 'lxml')

            # Extract meta information
            meta_info = [meta.attrs for meta in soup.find_all('meta')]

            # Extract body text
            body_text = soup.get_text(separator='\n', strip=True)

            return meta_info, body_text
        else:
            return [], ''

    def save_text_to_file(self, meta_info, body_text, organization_name):
        if meta_info or body_text:
            directory = "extracted_text"
            if not os.path.exists(directory):
                os.makedirs(directory)

            file_name = os.path.join(directory, f"{organization_name}_extracted_text.txt")
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write("Meta Information:\n")
                for meta_tag in meta_info:
                    file.write(str(meta_tag) + "\n")

                file.write("\nBody Text:\n")
                file.write(body_text + "\n")
        else:
            print(f"Skipping saving text file for {organization_name} as extraction was skipped.")

    def start_scanning(self):
        urls_to_visit = [self.base_url]
        while urls_to_visit and len(self.visited_urls) < self.max_urls_to_visit:
            url = urls_to_visit.pop(0)
            html_content = self.fetch_web_page(url)
            if html_content:
                meta_info, body_text = self.parse_web_page(html_content, url)
                self.save_text_to_file(meta_info, body_text, "extracted_text.txt")

                # Extract URLs from the current page and add them to the list of URLs to visit
                soup = BeautifulSoup(html_content, 'lxml')
                urls = [urljoin(url, link.get('href')) for link in soup.find_all('a', href=True)]
                for new_url in urls:
                    if new_url not in self.visited_urls and new_url not in urls_to_visit:
                        urls_to_visit.append(new_url)

def main():
    with open(r"C:\Users\Megha Patel\Documents\Split_By_Zipcode_JSON2\27722_data.json", "r") as f:  # Replace "your_json_file.json" with the path to your JSON file
        data = json.load(f)

    spider = PMTWebScannerSpider()
    for entry in data:
        organization_name = entry.get("Organization Name")
        website = entry.get("websites", {}).get(organization_name)
        if not website or any(domain in website for domain in ["guidestar.org", "propublica.org", "causeiq.com", "charitynavigator.org", "facebook.com"]):
            print(f"Skipping {organization_name} due to invalid website: {website}")
            continue

        print(f"Scanning website for {organization_name}: {website}")
        spider.base_url = website
        spider.start_scanning()
        meta_info, body_text = spider.parse_web_page(spider.fetch_web_page(website), website)
        spider.save_text_to_file(meta_info, body_text, organization_name)

if __name__ == "__main__":
    main()
