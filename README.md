# Community Resource Guide

This repository contains the Community Resource Guide, a comprehensive tool to help users find community resources, volunteer opportunities, fundraisers, and related information.

## Overview

The Community Resource Guide is a database of organizations in Durham, NC, allowing users to locate community resources, volunteer opportunities, and more.

## Features

- Comprehensive database of community organizations in Durham, NC.
- Search functionality to find specific organizations and resources.
- Detailed information about each organization's programs, mission, and impact.
- Suggested questions to guide users in their search for information.
- Interactive chatbot interface to answer user queries.

## Video Overview
[![Community Resource Guide Overview](https://img.youtube.com/vi/znj-yYIB2Gg/0.jpg)](https://youtu.be/znj-yYIB2Gg)

## Installation

### Prerequisites
- Python 3.8 or higher
- Streamlit
- Sentence Transformers
- OpenAI API key
- Google Cloud Storage credentials

### Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/Community-Resource-Guide.git
   cd Community-Resource-Guide
   ```

2. **Create and Activate a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
   ```

3. **Install the Required Packages**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Secrets**:
   - Set up a `secrets.toml` file in the Streamlit configuration directory with your OpenAI API key and Google Cloud Storage credentials:
     ```toml
     [secrets]
     OPENAI_API_KEY = "your_openai_api_key"
     GOOGLE_CLOUD_CREDENTIALS = "path_to_google_cloud_credentials.json"
     ```

## Running the Application

Navigate to the `community_resource` directory:

```bash
cd community_resource
```

Run the Streamlit application:

```bash
streamlit run app.py
```

## Usage

1. Open your web browser and navigate to the local address provided by Streamlit (usually `http://localhost:8501`).
2. Or, use the hosted version here: [Community Resource Guide](https://community-resource-guide-wvjkyatv3qce7ebgtvm2rf.streamlit.app/)
3. Interact with the chatbot to find information about community resources in Durham, NC.
4. Use the suggested questions for quick access to common queries.

## Data Structure

Data is stored in Google Cloud Storage in a JSON format, which we use as a vector database. Each entry includes:
- **URL**: Link to the organization's webpage or resource.
- **Meta Info**: Metadata, such as charset, generator type, image properties, and open graph tags.
- **Body Text**: Main text from the page.
- **Embeddings**: Numerical embeddings for efficient querying and similarity matching.
- **Is RFP**: Boolean indicating if the entry relates to a Request for Proposal (RFP), which helps categorize resources based on funding or proposal-related opportunities.

### Why Google Cloud Storage

We use Google Cloud Storage as a vector database because Google Cloud offers free storage credits each month, making it a cost-effective solution for our project. The embeddings allow us to perform semantic searches efficiently, enabling users to find relevant resources quickly.

Example JSON entry:
```json
{
  "url": "https://en.wikipedia.org/wiki/Podyachy",
  "meta_info": [{ "charset": "UTF-8" }, ...],
  "body_text": "Text about the resource...",
  "embeddings": [0.123, -0.456, ...],
  "is_rfp": false
}
```

## Future Goals

- **Error Handling**: Improve error handling to ensure smooth and reliable operation.
- **User Interface Enhancements**: Upgrade the user interface to be cleaner and more intuitive.
- **Expansion**: Broaden the scope of organizations to reach a wider audience beyond Durham, NC.

## MIT License

Copyright (c) 2024 meghamkpatel

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
