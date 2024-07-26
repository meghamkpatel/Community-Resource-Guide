from google.cloud import storage
from google.oauth2 import service_account
from sentence_transformers import SentenceTransformer
import json
import numpy as np
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity
import concurrent.futures  # Import concurrent.futures
from tqdm import tqdm  # Import tqdm for progress bars

# Initialize SentenceTransformer model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Load GCS credentials
gcs_credentials = {
    "type": "service_account",
    "project_id": st.secrets["gcs"]["project_id"],
    "private_key_id": st.secrets["gcs"]["private_key_id"],
    "private_key": st.secrets["gcs"]["private_key"].replace('\\n', '\n'),
    "client_email": st.secrets["gcs"]["client_email"],
    "client_id": st.secrets["gcs"]["client_id"],
    "auth_uri": st.secrets["gcs"]["auth_uri"],
    "token_uri": st.secrets["gcs"]["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["gcs"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["gcs"]["client_x509_cert_url"]
}

# Initialize Google Cloud Storage client with credentials
credentials = service_account.Credentials.from_service_account_info(gcs_credentials)
storage_client = storage.Client(credentials=credentials)
bucket_name = "community_resource_nc"
bucket = storage_client.bucket(bucket_name)

# Function to download a single blob
def download_blob(blob):
    try:
        content = blob.download_as_text()
        data = json.loads(content)
        return (blob.name, data)
    except json.JSONDecodeError:
        print(f"Skipping non-JSON blob: {blob.name}")
        return None
    except Exception as e:
        print(f"Error downloading blob {blob.name}: {str(e)}")
        return None

# Function to download blobs from GCS in parallel
def download_blobs(blobs, max_workers=10):
    documents = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_blob = {executor.submit(download_blob, blob): blob for blob in blobs}
        for future in tqdm(concurrent.futures.as_completed(future_to_blob), total=len(future_to_blob), desc="Downloading blobs"):
            try:
                result = future.result()
                if result:
                    documents.append(result)
            except Exception as e:
                print(f"Error in future: {str(e)}")
    return documents

# Function to generate embeddings using SentenceTransformer
def generate_embeddings(text):
    try:
        return embedding_model.encode(text).tolist()
    except Exception as e:
        print(f"Error generating embeddings: {str(e)}")
        return None

# Function to deduplicate documents
def deduplicate_documents(documents, similarity_threshold=0.85):
    unique_documents = []
    unique_vectors = []
    for name, doc in tqdm(documents, desc="Deduplicating documents"):
        text = doc.get("body_text", "")
        embeddings = generate_embeddings(text)
        if embeddings is None:
            continue
        is_unique = True
        for unique_vector in unique_vectors:
            if cosine_similarity([embeddings], [unique_vector])[0][0] > similarity_threshold:
                is_unique = False
                print(f"Deleting duplicate document: {name}")
                break
        if is_unique:
            unique_documents.append((name, doc))
            unique_vectors.append(embeddings)
    return unique_documents

# Function to upload cleaned data to GCS
def upload_cleaned_data(cleaned_documents):
    for i, (original_name, doc) in enumerate(tqdm(cleaned_documents, desc="Uploading cleaned data")):
        blob_name = f"cleaned_data/doc_{i}.json"
        blob = bucket.blob(blob_name)
        blob.upload_from_string(json.dumps(doc), content_type='application/json')
        print(f"Uploaded {blob_name}")

# Main function to clean the database
def clean_database(max_blobs=None, batch_size=100):
    blobs = list(bucket.list_blobs())
    if max_blobs:
        blobs = blobs[:max_blobs]

    total_blobs = len(blobs)
    print(f"Total blobs to process: {total_blobs}")

    for i in range(0, total_blobs, batch_size):
        batch_blobs = blobs[i:i + batch_size]
        print(f"Processing batch {i // batch_size + 1}/{(total_blobs // batch_size) + 1}")

        print("Downloading blobs...")
        documents = download_blobs(batch_blobs)
        print(f"Downloaded {len(documents)} documents in batch {i // batch_size + 1}")

        print("Deduplicating documents...")
        cleaned_documents = deduplicate_documents(documents)
        print(f"Reduced to {len(cleaned_documents)} unique documents in batch {i // batch_size + 1}")

        print("Uploading cleaned data...")
        upload_cleaned_data(cleaned_documents)
        print(f"Cleaned data uploaded successfully for batch {i // batch_size + 1}")

if __name__ == "__main__":
    # Specify a maximum number of blobs to process in this run (e.g., 1000)
    clean_database(max_blobs=1000, batch_size=100)