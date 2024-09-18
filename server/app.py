from flask import Flask, request, jsonify
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from google.cloud import storage
from google.oauth2 import service_account
import numpy as np
import json
import openai
import concurrent.futures
import csv
from datetime import datetime
from io import StringIO

app = Flask(__name__)
CORS(app)
with open('config.json') as config_file:
    config = json.load(config_file)

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

openai.api_key = config["general"]["openai_api_key"]

gcs_credentials = {
    "type": "service_account",
    "project_id": config["gcs"]["project_id"],
    "private_key_id": config["gcs"]["private_key_id"],
    "private_key": config["gcs"]["private_key"].replace('\\n', '\n'),
    "client_email": config["gcs"]["client_email"],
    "client_id": config["gcs"]["client_id"],
    "auth_uri": config["gcs"]["auth_uri"],
    "token_uri": config["gcs"]["token_uri"],
    "auth_provider_x509_cert_url": config["gcs"]["auth_provider_x509_cert_url"],
    "client_x509_cert_url": config["gcs"]["client_x509_cert_url"]
}

credentials = service_account.Credentials.from_service_account_info(gcs_credentials)
storage_client = storage.Client(credentials=credentials)
bucket_name = "community_resource_nc"
bucket = storage_client.bucket(bucket_name)

feedback_bucket_name = "feedback_crg"
feedback_bucket = storage_client.bucket(feedback_bucket_name)

def upload_feedback_to_gcs(feedback_data):
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["timestamp", "response_id", "feedback_type", "user_input", "bot_response", "issue", "additional_feedback"])
    writer.writerows(feedback_data)
    output.seek(0)

    blob = feedback_bucket.blob(f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    blob.upload_from_string(output.getvalue(), content_type='text/csv')

def generate_embeddings(text):
    try:
        return embedding_model.encode(text).tolist()
    except Exception as e:
        print(f"Error generating embeddings: {str(e)}")
        return None

def count_tokens(text):
    return len(text.split())

def get_blobs_from_gcs_paginated(max_blobs=500):
    blobs = []
    blob_iterator = bucket.list_blobs()
    for blob in blob_iterator:
        blobs.append(blob)
        if len(blobs) >= max_blobs:
            break
    return blobs

def search_similar_documents(query, top_k=100):
    query_vector = generate_embeddings(query)
    if query_vector is None:
        return []

    blobs = get_blobs_from_gcs_paginated()
    similarities = []

    def process_blob(blob):
        content = blob.download_as_text()
        try:
            data = json.loads(content)
            text = data.get("body_text", "")
            embeddings = data.get("embeddings", [])
            if not text.strip() or not embeddings:
                return None
            similarity = np.dot(query_vector, embeddings) / (np.linalg.norm(query_vector) * np.linalg.norm(embeddings))
            return (text, similarity)
        except json.JSONDecodeError:
            print(f"Skipping non-JSON blob: {blob.name}")
            return None

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_blob = {executor.submit(process_blob, blob): blob for blob in blobs}
        for future in concurrent.futures.as_completed(future_to_blob):
            result = future.result()
            if result:
                similarities.append(result)

    similarities.sort(key=lambda x: x[1], reverse=True)
    return [text for text, _ in similarities[:top_k]]

def generate_prompt(message_history):
    prompt_start = "Answer the question based on the context below. \n\nContext:\n"
    prompt_end = "\n\nAnswer:"

    user_query = message_history[-1]["content"]
    similar_docs = search_similar_documents(user_query)

    # Compile contexts into a single prompt, respecting character limits
    prompt = prompt_start
    for doc in similar_docs:
        if len(prompt + doc + prompt_end) < 3750:
            prompt += "\n\n---\n\n" + doc
        else:
            break

    # Include conversation history in the prompt
    for message in message_history:
        role = "User" if message["role"] == "user" else "Assistant"
        content = message["content"]
        prompt += f"\n\n{role}: {content}"

    prompt += prompt_end
    return prompt

def generate_openai_response(prompt, temperature=0.7):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that is an expert on community organizations in Durham, NC. Provide in-depth answers to questions about the organization's programs, mission, impact, and other related topics. Offer thorough explanations, detailed insights, and cover all relevant aspects to provide comprehensive responses. Include links to relevant resources if available. Ask follow-up questions to engage the user and provide specific examples."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.json
    messages = data.get('messages')

    if not messages or not isinstance(messages, list) or len(messages) == 0:
        return jsonify({"error": "No messages provided"}), 400

    if not messages[-1].get('content'):
        return jsonify({"error": "Invalid message format"}), 400

    final_prompt = generate_prompt(messages)
    bot_response = generate_openai_response(final_prompt)

    return jsonify({"response": bot_response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

