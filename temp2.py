<<<<<<< HEAD
import urllib.request
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.error import HTTPError
import numpy as np
import scipy
import requests

def fetch_web_page(url):
    try:
        response = requests.get(url, verify=False)  # Disable SSL certificate verification
        return response.text
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return None

def parse_web_page(html_content, base_url, visited_urls):
    if html_content is not None and base_url not in visited_urls:
        visited_urls.add(base_url)
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract meta information
        meta_info = [meta.attrs for meta in soup.find_all('meta')]
        
        # Extract body text
        body_text = soup.find('body').get_text(separator='\n', strip=True) if soup.find('body') else ''
        
        # Extract URLs
        urls = [urljoin(base_url, link.get('href')) for link in soup.find_all('a', href=True)]
        
        # Recursively parse content from URLs
        extracted_content = []
        for url in urls:
            html_content = fetch_web_page(url)
            if html_content:
                meta_info, body_text, _ = parse_web_page(html_content, url, visited_urls)
                extracted_content.append((url, meta_info, body_text))
        
        return meta_info, body_text, extracted_content
    else:
        return [], '', []

def save_text_to_file(meta_info, body_text, file_name):
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write("Meta Information:\n")
        for meta_tag in meta_info:
            file.write(str(meta_tag) + "\n")
        
        file.write("\nBody Text:\n")
        file.write(body_text + "\n")

def main():
    url = "https://www.keyeducation.com/"
    html_content = fetch_web_page(url)
    if html_content:
        visited_urls = set()
        meta_info, body_text, _ = parse_web_page(html_content, url, visited_urls)
        save_text_to_file(meta_info, body_text, "extracted_text.txt")

if __name__ == "__main__":
    main()
=======
import requests

# Test Case: Invalid API Key
def test_invalid_api_key(api_key):
    url = f"https://www.googleapis.com/customsearch/v1?q=test&key={api_key}&num=1"
    response = requests.get(url)
    print("Invalid API Key - Response Status Code:", response.status_code)
    print("Response Content:", response.content.decode("utf-8"))

# Test Case: Restricted API Key
def test_restricted_api_key(api_key):
    url = f"https://www.googleapis.com/customsearch/v1?q=test&key={api_key}&num=1"
    response = requests.get(url)
    print("Restricted API Key - Response Status Code:", response.status_code)
    print("Response Content:", response.content.decode("utf-8"))

# Test Case: Quota Limits
def test_quota_limits(api_key):
    url = f"https://www.googleapis.com/customsearch/v1?q=test&key={api_key}&num=1"
    response = requests.get(url)
    print("Quota Limits - Response Status Code:", response.status_code)
    print("Response Content:", response.content.decode("utf-8"))

# Test Case: Incorrect API Request
def test_incorrect_api_request(api_key):
    url = f"https://www.googleapis.com/customsearch/v1?q=test&num=1"  # Missing API key
    response = requests.get(url)
    print("Incorrect API Request - Response Status Code:", response.status_code)
    print("Response Content:", response.content.decode("utf-8"))

# Test Case: Network Issues
def test_network_issues(api_key):
    url = f"https://www.googleapis.com/customsearch/v1?q=test&key={api_key}&num=1"
    response = requests.get(url)
    print("Network Issues - Response Status Code:", response.status_code)
    print("Response Content:", response.content.decode("utf-8"))

# Test Case: Server-Side Errors
def test_server_side_errors(api_key):
    url = f"https://www.googleapis.com/customsearch/v1?q=test&key={api_key}&num=1"
    response = requests.get(url)
    print("Server-Side Errors - Response Status Code:", response.status_code)
    print("Response Content:", response.content.decode("utf-8"))

# Test Case: API Changes
def test_api_changes(api_key):
    url = f"https://www.googleapis.com/customsearch/v1?q=test&key={api_key}&num=1"
    response = requests.get(url)
    print("API Changes - Response Status Code:", response.status_code)
    print("Response Content:", response.content.decode("utf-8"))

if __name__ == "__main__":
    # Replace 'YOUR_API_KEY' with your actual API key obtained from the Google Cloud Console
    api_key = ""

    test_invalid_api_key(api_key)
    test_restricted_api_key(api_key)
    test_quota_limits(api_key)
    test_incorrect_api_request(api_key)
    test_network_issues(api_key)
    test_server_side_errors(api_key)
    test_api_changes(api_key)
>>>>>>> c371ee9210c5111d439b1bd1b7c04dd3ec58b61b
