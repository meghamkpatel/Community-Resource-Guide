import os
import json
from google.cloud import language_v1
from googlesearch import search
from google_auth_oauthlib.flow import InstalledAppFlow

# Function to obtain OAuth 2.0 credentials
def get_credentials():
    SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

    flow = InstalledAppFlow.from_client_secrets_file(
        r'C:\Users\Megha Patel\Documents\Community-Resource-Guide\client_secret.json', scopes=SCOPES)
    credentials = flow.run_local_server()

    return credentials

def extract_website_from_text(text, credentials):
    # Create a client using the obtained credentials
    client = language_v1.LanguageServiceClient(credentials=credentials)

    # Perform entity recognition on the text
    document = {"content": text, "type_": language_v1.Document.Type.PLAIN_TEXT}
    response = client.analyze_entities(request={'document': document})

    # Extract organization names from recognized entities
    organization_names = [entity.name for entity in response.entities if entity.type_.name == "ORGANIZATION"]

    # Search for the websites of the organizations
    websites = {}
    for org_name in organization_names:
        try:
            # Perform Google search and get the first result's URL
            search_results = search(org_name, num=1, stop=1)
            website_url = next(search_results)
            websites[org_name] = website_url
        except Exception as e:
            print(f"Error occurred while searching for {org_name}: {e}")

    return websites

def process_json_files(input_folder, output_folder, credentials):
    # Loop through each JSON file in the input folder
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            input_json_path = os.path.join(input_folder, filename)
            output_json_path = os.path.join(output_folder, filename)

            with open(input_json_path, 'r') as json_file:
                data = []
                for line in json_file:
                    try:
                        entry = json.loads(line.strip())
                        data.append(entry)
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON in file {input_json_path}: {e}")
                        continue

            # Process each JSON object in the file
            for entry in data:
                text = entry.get('text', '')  # Assuming 'text' is the key containing text to analyze
                websites = extract_website_from_text(text, credentials)
                entry['websites'] = websites

            # Save the updated JSON data to a new file
            with open(output_json_path, 'w') as output_json_file:
                for entry in data:
                    json.dump(entry, output_json_file)
                    output_json_file.write('\n')

# Get OAuth 2.0 credentials
credentials = get_credentials()

# Paths to input and output folders
input_folder = r'C:\Users\Megha Patel\Documents\Split_By_Zipcode_JSON'
output_folder = r'C:\Users\Megha Patel\Documents\Split_By_Zipcode_JSON2'

# Process JSON files in the input folder
process_json_files(input_folder, output_folder, credentials)
