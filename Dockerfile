# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install git
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Copy the project files into the container
COPY . .

# Install uv
RUN pip install uv

# Install dependencies
# Using --all-extras to install all optional dependencies
RUN uv sync --all-extras

# Expose the port the app runs on
EXPOSE 8000

# Define the command to run the application
# This is a placeholder command. You may need to update it depending on your application's entry point.
CMD ["uv", "run", "python", "-m", "src.utils.logger"]
