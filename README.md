
# Community Resource Guide - Web App

This project is a dual-purpose web application that includes a React frontend and a Flask backend. It serves as a Community Resource Guide and chatbot interface to help users find local resources and information.

## Project Structure

- **Frontend (React)**: Located in the `/src` folder.
- **Backend (Flask)**: Located in the `/server` folder.

## Prerequisites

Before running the app, make sure you have the following installed:

- **Node.js** (v14 or higher)
- **Python** (v3.8 or higher)
- **Docker** (if you prefer to use Docker)

## Installation

### Clone the Repository

```bash
git clone https://github.com/meghamkpatel/Community-Resource-Guide.git
cd Community-Resource-Guide
```

### Switch to the Correct Branch

```bash
git checkout comm-res-app-web
```


## Running the App

### 1. Running the React Frontend

Navigate to the root of the project, and install the dependencies for the frontend:

```bash
cd chat-bot-app
npm install
```

Start the React development server:

```bash
npm start
```

The React server will start at `http://localhost:3000`.

### 2. Running the Flask Backend

Open a new terminal window and navigate to the `server` directory:

```bash
cd server
```

Create a virtual environment and activate it (optional but recommended):

```bash
python3 -m venv venv
source venv/bin/activate 
```

Install the backend dependencies:

```bash
pip install -r requirements.txt
```

Run the Flask server using Gunicorn:

```bash
gunicorn --config gunicorn_config.py app:app
```

The Flask server will start at `http://localhost:5000`.

## Updating changes on resourceguide.io

Once you make changes to a component, the container that has these changes and the frontend as a whole, has to be moved to the ec2 instance that hosts the container.
1. Find the name of the container that runs on the ec2 instance. This can be done through sudo docker ps -a
2. Stop that container. Go back to your local system, push your container to Dockerhub (an org account will be created shortly), with the name being "{container-name-from-previous-step:DDMMYY}"
3. Pull the container from docker hub on the ec2 instance, and then deploy ON THE SAME PORT as before. These specific details will be updated very shortly.


