# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the default shell to bash for process substitution
SHELL ["/bin/bash", "-c"]

# Set the working directory in the container
WORKDIR /app

# Add arguments for user and group IDs, with defaults
ARG UID=1000
ARG GID=1000

# 1. Install system dependencies and uv as root
RUN apt-get update && \
    apt-get install -y git make libgomp1 && \
    rm -rf /var/lib/apt/lists/*

# Install uv using the recommended method
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 2. Install third-party dependencies from pyproject.toml
# This creates a cached layer that only changes when dependencies change.
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --all-extras

# 3. Copy the rest of the application code
COPY . .

# 4. Install the local application in editable mode
# --no-deps is used because we already installed dependencies
RUN uv pip install --system --no-deps -e .

# 5. Create a non-root user and group
RUN groupadd -g $GID -o appgroup && \
    useradd -m -u $UID -g $GID -s /bin/bash appuser

# 6. Change ownership of the entire app directory to the new user
RUN chown -R appuser:appgroup /app

# 7. Switch to the non-root user
USER appuser

# Expose the port the app runs on
EXPOSE 8000

# Keep the container running for development
CMD ["tail", "-f", "/dev/null"]
