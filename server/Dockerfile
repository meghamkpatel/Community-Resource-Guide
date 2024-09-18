# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn (if not included in requirements.txt)
RUN pip install gunicorn

# Copy the rest of the application code
COPY . .

# Expose the port that Gunicorn will run on
EXPOSE 8000

# Command to run the Gunicorn server
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]

