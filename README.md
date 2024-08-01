# Community Resource and BearBrown Bot

This repository contains two main applications: the **Community Resource Guide** and the **BearBrown Bot**. Both applications share similar elements but are designed for different purposes.

## Overview

### Community Resource Guide
The **Community Resource Guide** is a comprehensive database of organizations in Durham, NC. It helps users find community resources, volunteer opportunities, fundraisers, and other related information quickly and easily.

### BearBrown Bot
The **BearBrown Bot** is designed to be embedded on the BearBrown.co website. Its purpose is to assist users in finding resources and information within the BearBrown website, providing an enhanced and interactive user experience.

## Features

### Community Resource Guide
- Comprehensive database of community organizations in Durham, NC.
- Search functionality to find specific organizations and resources.
- Detailed information about each organization's programs, mission, impact, and more.
- Suggested questions to guide users in their search for information.
- Interactive chatbot interface to answer user queries.

### BearBrown Bot
- Embedded chatbot for the BearBrown.co website.
- Helps users find resources and information within the website.
- Provides detailed and interactive responses to user queries.
- Enhances user experience with guided suggestions and follow-up questions.

## Installation

### Prerequisites
- Python 3.8 or higher
- Streamlit
- Sentence Transformers
- OpenAI API key
- Google Cloud Storage credentials

### Setup

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/Community-Resource-and-BearBrown-Bot.git
   cd Community-Resource-and-BearBrown-Bot
   ```

2. Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   - Create a `.env` file in the root directory.
   - Add your OpenAI API key and Google Cloud Storage credentials to the `.env` file.

### Running the Applications

#### Community Resource Guide
1. Navigate to the `community_resource` directory:
   ```sh
   cd community_resource
   ```

2. Run the Streamlit application:
   ```sh
   streamlit run app.py
   ```

#### BearBrown Bot
1. Navigate to the `bearbrown_bot` directory:
   ```sh
   cd bearbrown_bot
   ```

2. Run the Streamlit application:
   ```sh
   streamlit run app.py
   ```

## Usage

### Community Resource Guide
1. Open your web browser and navigate to the local address provided by Streamlit (usually `http://localhost:8501`).
2. Interact with the chatbot to find information about community resources in Durham, NC.
3. Use the suggested questions to quickly get answers to common queries.

### BearBrown Bot
1. Embed the BearBrown Bot on the BearBrown.co website.
2. Users visiting the website can interact with the bot to find resources and information.
3. The bot will guide users through their queries and provide detailed responses and follow-up questions.

## Contributing

We welcome contributions to enhance the features and capabilities of both the Community Resource Guide and BearBrown Bot. Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch:
   ```sh
   git checkout -b feature/YourFeatureName
   ```
3. Make your changes and commit them:
   ```sh
   git commit -m "Add Your Feature"
   ```
4. Push to the branch:
   ```sh
   git push origin feature/YourFeatureName
   ```
5. Open a pull request describing your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any questions or inquiries, please contact us at:
- Website: [Community Resource](https://community-resource-guide-wvjkyatv3qce7ebgtvm2rf.streamlit.app/)
- Website: [BearBrown](https://bearbrown.co)
