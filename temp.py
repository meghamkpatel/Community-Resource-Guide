import os
import json
from google.cloud import language_v1
import requests
import time

# Function to obtain OAuth 2.0 credentials
def get_credentials():
    SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

    # Replace this with your code to obtain credentials if needed
    return None

# Function to extract website URL using Google Custom Search API
def search_with_api_key(search_query, api_key):
    url = f"https://www.googleapis.com/customsearch/v1?q={search_query}&key={api_key}&num=1"
    response = requests.get(url)
    data = response.json()
    if 'items' in data and len(data['items']) > 0:
        return data['items'][0]['link']
    else:
        return None

def extract_website_from_text(text, credentials, api_key):
    # Replace this with your code to analyze entities if needed
    # This function should return a list of organization names
    organization_names = [text]  # Dummy organization names for testing

    websites = {}
    print("Organization Names:")
    search_query = " ".join(organization_names)

    try:
        # Perform Google search with API key
        website_url = search_with_api_key(search_query, api_key)
        if website_url:
            websites[search_query] = website_url
        else:
            print(f"No website found for {search_query}")
    except Exception as e:
        print(f"Error occurred while searching for {search_query}: {e}")

    return websites

def process_json_files(input_folder, output_folder, credentials, apikey):
    # Loop through each JSON file in the input folder
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            input_json_path = os.path.join(input_folder, filename)
            output_json_path = os.path.join(output_folder, filename)

            with open(input_json_path, 'r') as json_file:
                data = json.load(json_file)  # Load the entire file as a list of dictionaries
                
                # Process each JSON object in the file
                for entry in data:
                    text = entry.get('Organization Name', '')  # Assuming 'text' is the key containing text to analyze
                    websites = extract_website_from_text(text, credentials, apikey)
                    entry['websites'] = websites

            # Save the updated JSON data to a new file
            with open(output_json_path, 'w') as output_json_file:
                json.dump(data, output_json_file, indent=4)  # Dump the entire list of dictionaries


# Get OAuth 2.0 credentials if needed
credentials = get_credentials()

# Replace 'YOUR_API_KEY' with your actual API key
api_key = ""

# Paths to input and output folders
input_folder = r'C:\Users\Megha Patel\Documents\Split_By_Zipcode_JSON'
output_folder = r'C:\Users\Megha Patel\Documents\Split_By_Zipcode_JSON2'

# Process JSON files in the input folder
process_json_files(input_folder, output_folder, credentials, api_key)
