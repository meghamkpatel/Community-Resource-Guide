import urllib.request
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.error import HTTPError
import numpy as np
import scipy
import requests

class PMTWebScannerSpider:
    def __init__(self):
        self.visited_urls = set()
        self.base_url = "https://www.madeindurham.org/"  # Base URL for beauty products
        self.max_urls_to_visit = 300  # Maximum number of URLs to visit

    def fetch_web_page(self, url):
        try:
            response = requests.get(url, verify=False, timeout=10)  # Timeout set to 10 seconds
            return response.text
        except Exception as e:
            print(f"Error fetching URL: {e}")
            return None

    def parse_web_page(self, html_content, url):
        if html_content is not None and url not in self.visited_urls:
            self.visited_urls.add(url)
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract meta information
            meta_info = [meta.attrs for meta in soup.find_all('meta')]

            # Extract body text
            body_text = soup.get_text(separator='\n', strip=True)

            return meta_info, body_text
        else:
            return [], ''

    def save_text_to_file(self, meta_info, body_text, file_name):
        with open(file_name, 'a', encoding='utf-8') as file:  # Change 'w' to 'a' to append to file
            file.write("Meta Information:\n")
            for meta_tag in meta_info:
                file.write(str(meta_tag) + "\n")

            file.write("\nBody Text:\n")
            file.write(body_text + "\n")

    def start_scanning(self):
        urls_to_visit = [self.base_url]
        while urls_to_visit and len(self.visited_urls) < self.max_urls_to_visit:
            url = urls_to_visit.pop(0)
            html_content = self.fetch_web_page(url)
            if html_content:
                meta_info, body_text = self.parse_web_page(html_content, url)
                self.save_text_to_file(meta_info, body_text, "extracted_text.txt")

                # Extract URLs from the current page and add them to the list of URLs to visit
                soup = BeautifulSoup(html_content, 'html.parser')
                urls = [urljoin(url, link.get('href')) for link in soup.find_all('a', href=True)]
                for new_url in urls:
                    if new_url not in self.visited_urls and new_url not in urls_to_visit:
                        urls_to_visit.append(new_url)

def main():
    spider = PMTWebScannerSpider()
    spider.start_scanning()

if __name__ == "__main__":
    main()
