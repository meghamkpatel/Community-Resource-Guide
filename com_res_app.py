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
import csv
from datetime import datetime
from io import StringIO

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
bucket_name = "community_resource_db"
bucket = storage_client.bucket(bucket_name)

# Initialize feedback bucket
feedback_bucket_name = "feedbackcrg"
feedback_bucket = storage_client.bucket(feedback_bucket_name)

# Function to upload feedback to GCS
def upload_feedback_to_gcs(feedback_data):
    # Convert feedback data to CSV format
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["timestamp", "response_id", "feedback_type", "user_input", "bot_response", "issue", "additional_feedback"])
    writer.writerows(feedback_data)
    output.seek(0)

    # Create a blob and upload the feedback CSV
    blob = feedback_bucket.blob(f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    blob.upload_from_string(output.getvalue(), content_type='text/csv')

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
def get_blobs_from_gcs_paginated(max_blobs=500):
    blobs = []
    blob_iterator = bucket.list_blobs()
    for blob in blob_iterator:
        blobs.append(blob)
        if len(blobs) >= max_blobs:
            break
    return blobs

def search_similar_documents(query, top_k=100):
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

def generate_prompt(query, history):
    """Generates a comprehensive prompt including contexts from similar documents and conversation history."""
    prompt_start = "Answer the question based on the context below. Provide a comprehensive and exhaustive list of all potential organizations that can help. \n\nContext:\n"
    prompt_end = f"\n\nQuestion: {query}\nAnswer:"
    
    similar_docs = search_similar_documents(query)

    # Compile contexts into a single prompt, respecting character limits
    prompt = prompt_start
    for doc in similar_docs:
        if len(prompt + doc + prompt_end) < 3750:
            prompt += "\n\n---\n\n" + doc
        else:
            break

    # Include conversation history in the prompt
    for message in history:
        role = message["role"]
        content = message["content"]
        prompt += f"\n\n{role.capitalize()}: {content}"

    prompt += prompt_end
    return prompt

def generate_openai_response(messages, temperature=0.7):
    """Generates a response from OpenAI based on a structured prompt."""
    try:
        response = client.chat.completions.create(
            model="ft:gpt-4o-mini-2024-07-18:skunks-ai::9un3mrZs",
            messages=messages,
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
if 'response_ids' not in st.session_state:
    st.session_state.response_ids = []
if 'feedback' not in st.session_state:
    st.session_state.feedback = {}
if 'feedback_data' not in st.session_state:
    st.session_state.feedback_data = []

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

    # Create the messages payload for OpenAI API
    messages = [{"role": "system", "content": "You are an assistant that is an expert on community organizations in Durham, NC. For main queries related to specific needs such as homelessness, food shelters, education, and similar, provide a comprehensive and exhaustive list of all potential organizations that can help. Include each organization's verified contact information and a brief overview of what the organization does. Where available, include links to relevant resources. For other queries, provide information on the most relevant organization or organizations based on the user's needs. If specific information is not available, clearly indicate that and suggest checking with the organization directly for more details. Provide more detailed information about the organization's programs, mission, and impact only if specifically asked. Ensure your responses are thorough, clear, and concise, tailored to the user's query, and prioritize user safety and privacy. Aim to offer the most relevant and useful information to fully address the user's needs."}]
    for message in st.session_state.message_history:
        messages.append({"role": message["role"], "content": message["content"]})

    bot_response = generate_openai_response(messages)
    
    # Add assistant's response to history
    response_id = len(st.session_state.message_history)  # Unique ID for each response
    st.session_state.message_history.append({"role": "assistant", "content": bot_response, "id": response_id, "user_input": st.session_state.user_input})
    st.session_state.response_ids.append(response_id)

    # Clear text input
    clear_text_input()

    # Clear the session user input after processing
    st.session_state.user_input = ''

# Display chat messages from history on app rerun
for message in st.session_state.message_history:
    role = "user" if message["role"] == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message["content"])
        if role == "assistant":
            response_id = message.get("id")
            user_input = message.get("user_input")
            bot_response = message.get("content")
            col1, col2, col3 = st.columns([10, 1, 1])
            with col2:
                if st.button("👍", key=f"thumbs_up_{response_id}"):
                    st.session_state.feedback_data.append([
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                        response_id, 
                        "up", 
                        user_input, 
                        bot_response, 
                        "", 
                        ""
                    ])
                    upload_feedback_to_gcs(st.session_state.feedback_data)  # Upload the positive feedback immediately
                    st.session_state.feedback_data = []  # Clear the feedback data after upload
                    st.success("Thank you for your feedback!")
            with col3:
                if st.button("👎", key=f"thumbs_down_{response_id}"):
                    st.session_state.feedback[response_id] = {
                        "user_input": user_input, 
                        "bot_response": bot_response, 
                        "feedback": "",
                        "additional_feedback": ""
                    }
                    st.session_state.show_feedback_form = response_id

if 'show_feedback_form' in st.session_state:
    response_id = st.session_state.show_feedback_form
    feedback_entry = st.session_state.feedback.get(response_id, {})
    if feedback_entry:
        st.markdown(f"**Feedback for response to your question:** {feedback_entry['user_input']}")
        issue = st.selectbox("What was the issue?", ["Select an issue", "Hallucinating", "Not complete answer", "Very wrong answer"], key=f"issue_{response_id}")
        additional_feedback = st.text_area("Additional feedback (optional):", key=f"additional_feedback_{response_id}")

        if st.button("Submit Feedback", key=f"submit_feedback_{response_id}"):
            feedback_entry["feedback"] = issue
            feedback_entry["additional_feedback"] = additional_feedback

            st.session_state.feedback_data.append([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                response_id,
                "down",
                feedback_entry["user_input"],
                feedback_entry["bot_response"],
                feedback_entry["feedback"],
                feedback_entry["additional_feedback"]
            ])

            upload_feedback_to_gcs(st.session_state.feedback_data)
            st.session_state.feedback_data = []  # Clear the feedback data after upload
            st.success("Thank you for your feedback!")
            del st.session_state.show_feedback_form
