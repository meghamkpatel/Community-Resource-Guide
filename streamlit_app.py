import streamlit as st
from st_files_connection import FilesConnection
from openai import OpenAI
from dotenv import load_dotenv
from google.cloud import storage
from PyPDF2 import PdfReader
import numpy as np
import json
import os

# Set Streamlit page configuration
st.set_page_config(
    page_title="Made In Durham",
    page_icon="🤝",
    layout="wide",
)

# Load environment variables
load_dotenv()

# Initialize OpenAI services
client = OpenAI(api_key=st.secrets["general"]["openai_api_key"])


# Google Cloud Storage configuration
bucket_name = "durham-bot"

# Create connection object for Google Cloud Storage
conn = st.connection('gcs', type=FilesConnection)


# Initialize Google Cloud Storage client
storage_client = storage.Client()
bucket = storage_client.bucket(bucket_name)

# Function to generate embeddings
def generate_embeddings(text):
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

st.title("Made in Durham")

if 'user_input' not in st.session_state:
    st.session_state.user_input = ''

# Function to retrieve and parse text files from GCS
def get_texts_from_gcs():
    files = conn.list_files("text_files/")
    texts = []
    for file in files:
        text = conn.read(file, input_format="txt")
        texts.append(text)
    return texts

# Function to retrieve and parse text files from GCS
def get_texts_from_gcs():
    blobs = bucket.list_blobs(prefix="text_files/")
    texts = []
    for blob in blobs:
        text = blob.download_as_text()
        texts.append(text)
    return texts

def search_similar_documents(query, top_k=5):
    """Searches for documents in GCS that are similar to the query."""
    query_vector = generate_embeddings(query)
    texts = get_texts_from_gcs()
    
    # Compute similarity scores
    similarities = []
    for text in texts:
        text_vector = generate_embeddings(text)
        similarity = np.dot(query_vector, text_vector) / (np.linalg.norm(query_vector) * np.linalg.norm(text_vector))
        similarities.append((text, similarity))
    
    # Sort and return top_k similar documents
    similarities.sort(key=lambda x: x[1], reverse=True)
    return [text for text, _ in similarities[:top_k]]

def generate_prompt(query):
    """Generates a comprehensive prompt including contexts from similar documents."""
    prompt_start = (
        "Answer the question based on the context below. "
        "Provide detailed and in-depth responses. Explain thoroughly and cover all relevant aspects. "
        "Include links to relevant resources if available. Ask follow-up questions to engage the user and provide specific examples.\n\nContext:\n"
    )
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
                {"role": "system", "content": (
                        "You are an assistant that is an expert on the Made in Durham organization. "
                        "Provide in-depth answers to questions about the organization's programs, mission, impact, and other related topics. "
                        "Offer thorough explanations, detailed insights, and cover all relevant aspects to provide comprehensive responses. "
                        "Include links to relevant resources if available. Ask follow-up questions to engage the user and provide specific examples."
                    )},
                {"role": "user", "content": prompt}
            ] + [
                {"role": "user" if msg['role'] == 'You' else "assistant", "content": msg['content']}
                for msg in st.session_state.message_history
            ],
            temperature=temperature
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred: {str(e)}"

# User input for chat
user_input = st.chat_input("Ask me a question")

# Initialize or load message history
if 'message_history' not in st.session_state:
    st.session_state.message_history = []

def clear_text_input():
    """Function to clear text input."""
    st.session_state.text_input = ''

if user_input:
    # Add user's message to history
    st.session_state.message_history.append({"role": "user", "content": user_input})

    final_prompt = generate_prompt(user_input)
    bot_response = generate_openai_response(final_prompt)
    
    # Add assistant's response to history
    st.session_state.message_history.append({"role": "assistant", "content": bot_response})

    # Clear text input
    clear_text_input()

    # Display chat messages from history on app rerun
    for message in st.session_state.message_history:
        role = "user" if message["role"] == "user" else "assistant"
        with st.chat_message(role):
            st.markdown(message["content"])
