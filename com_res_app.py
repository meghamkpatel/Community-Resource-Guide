import streamlit as st
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from google.cloud import storage
from google.oauth2 import service_account
import numpy as np
import json
import os
from openai import OpenAI
import concurrent.futures

# Set Streamlit page configuration
st.set_page_config(
    page_title="Community Resources Guide",
    page_icon="🤝",
    layout="wide",
)

# Initialize SentenceTransformer model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

client = OpenAI(api_key=st.secrets["general"]["openai_api_key"])

# Extract GCS credentials from Streamlit secrets
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

# Function to generate embeddings using SentenceTransformer
def generate_embeddings(text):
    try:
        return embedding_model.encode(text).tolist()
    except Exception as e:
        print(f"Error generating embeddings: {str(e)}")
        return None

# Function to count tokens
def count_tokens(text):
    """Counts the tokens in the text."""
    return len(text.split())

st.title("Community Resource Guide")

if 'user_input' not in st.session_state:
    st.session_state.user_input = ''

# Suggested questions for the user to click on
suggested_questions = [
    "Can you suggest some volunteer opportunities in the Durham area?",
    "Are there any ongoing fundraisers for local nonprofits in Durham?",
    "Where can I find food banks in Durham?",
    "What resources are available for job seekers in Durham?",
    "Can you help me find mental health services in Durham?"
]

# Display suggested questions as buttons
st.sidebar.subheader("Suggested Questions")
for question in suggested_questions:
    if st.sidebar.button(question):
        st.session_state.user_input = question

# Function to retrieve blobs from GCS with manual pagination
def get_blobs_from_gcs_paginated(max_blobs=100):
    blobs = []
    blob_iterator = bucket.list_blobs()
    for blob in blob_iterator:
        blobs.append(blob)
        if len(blobs) >= max_blobs:
            break
    return blobs

def search_similar_documents(query, top_k=5):
    """Searches for documents in GCS that are similar to the query."""
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

def generate_prompt(query):
    """Generates a comprehensive prompt including contexts from similar documents."""
    prompt_start = "Answer the question based on the context below. \n\nContext:\n"
    prompt_end = f"\n\nQuestion: {query}\nAnswer:"
    
    similar_docs = search_similar_documents(query)

    # Compile contexts into a single prompt, respecting character limits
    prompt = prompt_start
    for doc in similar_docs:
        if len(prompt + doc + prompt_end) < 3750:
            prompt += "\n\n---\n\n" + doc
        else:
            break
    prompt += prompt_end
    return prompt

def generate_openai_response(prompt, temperature=0.7):
    """Generates a response from OpenAI based on a structured prompt."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content":"You are an assistant that is an expert on community organizations in Durham, NC. Provide in-depth answers to questions about the organization's programs, mission, impact, and other related topics. Offer thorough explanations, detailed insights, and cover all relevant aspects to provide comprehensive responses. Include links to relevant resources if available. Ask follow-up questions to engage the user and provide specific examples."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred: {str(e)}"

# User input for chat
user_input = st.chat_input("Ask me a question")

# Initialize or load message history
if 'message_history' not in st.session_state:
    st.session_state.message_history = []

# Add an introduction message from the bot
if 'bot_intro' not in st.session_state:
    st.session_state.bot_intro = True
    st.session_state.message_history.append({"role": "assistant", "content": "Hello! I'm your Community Resources Guide bot. I can help you find information about community organizations, volunteer opportunities, fundraisers, and more in Durham, NC. How can I assist you today?"})

def clear_text_input():
    """Function to clear text input."""
    st.session_state.text_input = ''

if st.session_state.user_input or user_input:
    # Handle the user input from both the text input and suggested questions
    if user_input:
        st.session_state.user_input = user_input

    # Add user's message to history
    st.session_state.message_history.append({"role": "user", "content": st.session_state.user_input})

    final_prompt = generate_prompt(st.session_state.user_input)
    bot_response = generate_openai_response(final_prompt)
    
    # Add assistant's response to history
    st.session_state.message_history.append({"role": "assistant", "content": bot_response})

    # Clear text input
    clear_text_input()

    # Clear the session user input after processing
    st.session_state.user_input = ''

# Display chat messages from history on app rerun
for message in st.session_state.message_history:
    role = "user" if message["role"] == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message["content"])
