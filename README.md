
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

## Running with Docker

If you prefer to run the entire application with Docker, you can use the `docker-compose.yml` file provided in the root of the project.

1. Make sure Docker is running.
2. Run the following command to build and start the services:

```bash
docker-compose up --build
```

The React frontend will be accessible at `http://localhost:3000`, and the Flask backend will run at `http://localhost:5000`.


