import streamlit as st
from dotenv import load_dotenv
from google.cloud import storage
from google.oauth2 import service_account
import numpy as np
import json
import os
import time
import faiss
from sentence_transformers import SentenceTransformer

# Set Streamlit page configuration
st.set_page_config(
    page_title="Made In Durham",
    page_icon="🤝",
    layout="wide",
)

# Load environment variables
load_dotenv()

# Initialize the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

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
bucket_name = "durham-bot"
bucket = storage_client.bucket(bucket_name)

# Function to generate embeddings
def generate_embeddings(text):
    try:
        embedding = model.encode(text)
        return embedding
    except Exception as e:
        st.error(f"Error generating embeddings: {str(e)}")
        return None

# Function to count tokens
def count_tokens(text):
    """Counts the tokens in the text."""
    return len(text.split())

st.title("Made in Durham")

if 'user_input' not in st.session_state:
    st.session_state.user_input = ''

def get_suggested_questions(query, top_k=5):
    """Fetches suggested questions based on the user's query."""
    return [
        "What is the organization about?",
        "What is the start date of the next cohort?",
        "What is the application process?",
        "What are the benefits of participating?",
        "Are there any prerequisites to join?"
    ]

# Function to retrieve blobs from GCS
def get_blobs_from_gcs():
    return list(bucket.list_blobs())

def build_faiss_index(blobs):
    """Builds a Faiss index from GCS blobs."""
    embeddings = []
    texts = []
    for blob in blobs:
        content = blob.download_as_text()
        try:
            data = json.loads(content)
            text = data.get("body_text", "")
            embedding = data.get("embeddings", [])
            if not text.strip() or not embedding:
                continue
            embeddings.append(embedding)
            texts.append(text)
        except json.JSONDecodeError:
            st.warning(f"Skipping non-JSON blob: {blob.name}")
    
    # Convert to numpy array
    embeddings = np.array(embeddings).astype('float32')
    
    # Create Faiss index
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    
    return index, texts

def search_similar_documents(query, index, texts, top_k=5):
    """Searches for documents in GCS that are similar to the query."""
    query_vector = generate_embeddings(query)
    if query_vector is None:
        return []
    
    query_vector = np.array(query_vector).astype('float32').reshape(1, -1)
    distances, indices = index.search(query_vector, top_k)
    
    similar_texts = [texts[i] for i in indices[0]]
    return similar_texts

def generate_prompt(query, index, texts):
    """Generates a comprehensive prompt including contexts from similar documents."""
    prompt_start = "Answer the question based on the context below. \n\nContext:\n"
    prompt_end = f"\n\nQuestion: {query}\nAnswer:"
    
    similar_docs = search_similar_documents(query, index, texts)

    # Compile contexts into a single prompt, respecting character limits
    prompt = prompt_start
    for doc in similar_docs:
        if len(prompt + doc + prompt_end) < 3750:
            prompt += "\n\n---\n\n" + doc
        else:
            break
    prompt += prompt_end
    return prompt

def generate_openai_response_typing(prompt, temperature=0.7):
    """Generates a response from OpenAI based on a structured prompt with typing effect."""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that is an expert on the Made in Durham organization. Provide in-depth answers to questions about the organization's programs, mission, impact, and other related topics. Offer thorough explanations, detailed insights, and cover all relevant aspects to provide comprehensive responses. Include links to relevant resources if available. Ask follow-up questions to engage the user and provide specific examples."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"An error occurred: {str(e)}"

def display_typing_effect(text, container):
    """Displays text with a typing effect."""
    full_text = ""
    for char in text:
        full_text += char
        container.markdown(full_text)
        time.sleep(0.01)  # Faster typing effect

# User input for chat
user_input = st.chat_input("Ask me a question")

def handle_suggested_question(question):
    st.session_state.user_input = question

# Display suggested questions
suggested_questions = get_suggested_questions(user_input)
if suggested_questions:
    st.write("Suggested Questions:")
    for question in suggested_questions:
        if st.button(question, key=question):
            handle_suggested_question(question)

# Initialize or load message history
if 'message_history' not in st.session_state:
    st.session_state.message_history = []

if 'faiss_index' not in st.session_state or 'faiss_texts' not in st.session_state:
    blobs = get_blobs_from_gcs()
    st.session_state.faiss_index, st.session_state.faiss_texts = build_faiss_index(blobs)

def clear_text_input():
    """Function to clear text input."""
    st.session_state.text_input = ''

if user_input:
    # Add user's message to history
    st.session_state.message_history.append({"role": "user", "content": user_input})

    final_prompt = generate_prompt(user_input, st.session_state.faiss_index, st.session_state.faiss_texts)
    bot_response = generate_openai_response_typing(final_prompt)
    
    # Add assistant's response to history
    st.session_state.message_history.append({"role": "assistant", "content": bot_response})

    # Clear text input
    clear_text_input()

# Display chat messages from history on app rerun
for message in st.session_state.message_history[:-1]:
    role = "user" if message["role"] == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message["content"])

# Display the latest message with typing effect
if st.session_state.message_history:
    latest_message = st.session_state.message_history[-1]
    if latest_message["role"] == "assistant":
        with st.chat_message("assistant"):
            placeholder = st.empty()
            display_typing_effect(latest_message["content"], placeholder)
    else:
        with st.chat_message("user"):
            st.markdown(latest_message["content"])
