import requests
import json
from urllib.parse import quote_plus
from time import sleep
from warcio.archiveiterator import ArchiveIterator

# The URL of the Common Crawl Index server
CC_INDEX_SERVER = 'http://index.commoncrawl.org/'

# The URL you want to look up in the Common Crawl index
TARGET_URL = 'https://www.madeindurham.org/'  # Replace with your target URL

def get_recent_indexes(n=20):
    index_list_url = 'https://index.commoncrawl.org/collinfo.json'
    response = requests.get(index_list_url)
    if response.status_code == 200:
        indexes = response.json()
        # Sort indexes by creation date and select the most recent `n` indexes
        indexes.sort(key=lambda x: x['id'], reverse=True)
        return [index['id'] for index in indexes[:n]]
    else:
        print(f"Error fetching index list: {response.status_code}")
        return []

def search_cc_index(url, index):
    encoded_url = quote_plus(url)
    index_url = f'{CC_INDEX_SERVER}{index}-index?url={encoded_url}&output=json'
    retries = 5
    for i in range(retries):
        try:
            print(f"Querying URL: {index_url}")
            response = requests.get(index_url)
            if response.status_code == 200:
                records = response.text.strip().split('\n')
                return [json.loads(record) for record in records if record.strip()]
            elif response.status_code == 404:
                print(f"No captures found for: {url} in index {index}")
                return []
            else:
                print(f"Error querying index {index}: {response.status_code}")
                sleep(2 ** i)  # Exponential backoff
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}. Retrying...")
            sleep(2 ** i)  # Exponential backoff
    return None

def search_multiple_indexes(url, indexes):
    all_records = []
    found_in_indexes = []
    for index in indexes:
        records = search_cc_index(url, index)
        if records:
            all_records.extend(records)
            found_in_indexes.append(index)
    return all_records, found_in_indexes

def fetch_page_from_cc(records):
    for record in records:
        offset, length = int(record['offset']), int(record['length'])
        s3_url = f'https://data.commoncrawl.org/{record["filename"]}'
        response = requests.get(s3_url, headers={'Range': f'bytes={offset}-{offset+length-1}'}, stream=True)
        if response.status_code == 206:
            warc_record = next(ArchiveIterator(response.raw))
            if warc_record.rec_type == 'response':
                content = warc_record.content_stream().read()
                if b'301 Moved Permanently' in content or b'302 Found' in content:
                    # Extract the Location header and follow the redirect
                    headers = dict(warc_record.http_headers.headers)
                    if 'Location' in headers:
                        redirect_url = headers['Location']
                        print(f"Following redirect to {redirect_url}")
                        final_response = requests.get(redirect_url)
                        if final_response.status_code == 200:
                            return final_response.content
                else:
                    return content
        else:
            print(f"Failed to fetch data: {response.status_code}")
    return None

# Fetch the most recent 20 indexes
indexes = get_recent_indexes(20)
print(f"Using indexes: {indexes}")

# Search the indexes for the target URL
records, found_in_indexes = search_multiple_indexes(TARGET_URL, indexes)
if records:
    print(f"Found {len(records)} records across multiple indexes")
    print(f"The URL was found in the following indexes: {found_in_indexes}")

    # Fetch the page content from the first record
    content = fetch_page_from_cc(records)
    if content:
        print(f"Successfully fetched content for {TARGET_URL}")
        print(content.decode('utf-8', errors='ignore'))  # Assuming the content is in UTF-8 encoding
else:
    print(f"No records found for {TARGET_URL}")
