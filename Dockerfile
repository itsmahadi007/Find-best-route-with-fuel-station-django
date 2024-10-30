# Use an official Python runtime as a parent image
FROM python:3.7.9

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Create directory for the app
RUN mkdir -p /app/backend
WORKDIR /app/backend

# Copy the current directory contents into the container at /app/backend
COPY . /app/backend

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose the port the app runs on
EXPOSE 8000
