
# Community Resource Guide - Web App

This project is a dual-purpose web application that includes a React frontend and a Flask backend. It serves as a Community Resource Guide and chatbot interface to help users find local resources and information.

## Project Structure

- **Frontend (React)**: Located in the `/src` folder.
- **Backend (Flask)**: Located in the `/server` folder.

## Prerequisites

Before running the app, ensure you have the following installed:

- **Node.js** (v14 or higher)
- **Python** (v3.8 or higher)
- **Docker** (optional, if you prefer to use Docker)

## Installation

### 1. Clone the Repository

\`\`\`bash
git clone https://github.com/meghamkpatel/Community-Resource-Guide.git
cd Community-Resource-Guide
\`\`\`

### 2. Switch to the Correct Branch

\`\`\`bash
git checkout comm-res-app-web
\`\`\`

## Running the App

### 1. Running the React Frontend

Navigate to the root of the project and install the dependencies for the frontend:

\`\`\`bash
cd chat-bot-app
npm install
\`\`\`

Start the React development server:

\`\`\`bash
npm start
\`\`\`

The React server will start at \`http://localhost:3000\`.

### 2. Running the Flask Backend

Open a new terminal window and navigate to the \`server\` directory:

\`\`\`bash
cd server
\`\`\`

Create a virtual environment and activate it (optional but recommended):

\`\`\`bash
python3 -m venv venv
source venv/bin/activate
\`\`\`

Install the backend dependencies:

\`\`\`bash
pip install -r requirements.txt
\`\`\`

Run the Flask server using Gunicorn:

\`\`\`bash
gunicorn --config gunicorn_config.py app:app
\`\`\`

The Flask server will start at \`http://localhost:5000\`.

## Updating Changes on \`resourceguide.io\`
Docker Account Details: https://hub.docker.com/repositories/humanaidockerhub
Ask for the credentials from the project manager!

### 1. Log in to the AWS Instance

Use the credentials shared with you to log in to the AWS instance. This instance can be located using the public IP displayed on the AWS EC2 Dashboard. **Note:** When the instance is shut down, its IP changes. You need to rebuild the React image to point to the new IP.

### 2. Update the IP in the Local React App

Navigate to your local installation:

\`\`\`bash
cd chat-bot-app/src
nano app.js
\`\`\`

Change the IP to the current public IP of the instance.

### 3. Build the Docker Image
Note: Follow this command instead: sudo docker build -t humanaidockerhub/comm-res-frontend-oct3-ipchange .

\`\`\`bash
docker build -t humanaidockerhub/comm-res-frontend-DATE-IPCHANGE .
\`\`\`

Replace \`DATE\` with the date of the change and \`IPCHANGE\` with a brief reason for rebuilding the container.

**Example:**

\`\`\`bash
docker build -t humanaidockerhub/comm-res-frontend-122724-IPCHANGE .
\`\`\`

### 4. Push the Updated Docker Image

\`\`\`bash
docker push humanaidockerhub/comm-res-frontend-122724-IPCHANGE
\`\`\`

### 5. SSH into the AWS Instance and Pull the Updated Docker Image

Navigate to the AWS Console, click the "Connect" button, and copy the SSH command into your console, ensuring the \`.pem\` file is in the same folder. This should log you in to the instance.

### 6. Load Docker Images and Move Required Files

1. **Install Docker on the Instance (if not already installed):**

   \`\`\`bash
   sudo apt-get update
   sudo apt-get install docker.io
   \`\`\`

2. **Pull the Docker Image:**

   \`\`\`bash
   sudo docker pull humanaidockerhub/comm-res-frontend-DATE-IPCHANGE
   \`\`\`

3. **Run the Docker Container:**

   \`\`\`bash
   sudo docker run -d -p 80:80 --name frontend humanaidockerhub/comm-res-frontend-DATE-IPCHANGE
   \`\`\`

4. **Access the React App:** Visit \`http://<public_ip>\` to access the running React app.

### 7. Verify the Backend Server Connection

1. **Ensure the React app is making calls to \`public_ip:8000\`.** Check this by inspecting the network tab in the browser tools (Right-click -> Inspect -> Network tab) while interacting with the app.
2. **If the IP is correct, proceed to set up the backend server.**

### 8. Set Up the Flask Backend on the AWS Instance

1. **Copy the server folder to the EC2 instance using SCP:**

   \`\`\`bash
   scp -i comm_resource_new.pem -r /path/to/chat-bot-app/server ec2-user@<public_ip>:/home/ec2-user
   \`\`\`

   Replace \`<public_ip>\` and the path to the \`.pem\` file as needed.

2. **Pull the PyTorch Docker Image on the EC2 Instance:**

   \`\`\`bash
   sudo docker pull pytorch/pytorch:latest
   \`\`\`

3. **Run the PyTorch Container:**

   \`\`\`bash
   sudo docker run -it --name my_pytorch_container -p 8000:5000 pytorch/pytorch:latest /bin/bash
   \`\`\`

4. **Copy the \`server\` folder into the running container:**

   \`\`\`bash
   sudo docker cp server my_pytorch_container:/server
   \`\`\`

5. **Navigate into the running Docker container:**

   \`\`\`bash
   sudo docker exec -it my_pytorch_container /bin/bash
   \`\`\`

6. **Start the Flask server:**

   \`\`\`bash
   cd /server
   gunicorn --bind 0.0.0.0:8000 app:app
   \`\`\`

### 9. Final Verification

Reload \`http://<public_ip>\` and check if API calls are correctly reaching the server.

### 10. Connect to \`resourceguide.io\`

1. **Log in to Namecheap (ask the project manager for DNS login details).**
2. **Edit the A record to point to the new IP address.**
3. Once updated, \`resourceguide.io\` will point to the instance!
