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

# Copy project dependency files
COPY pyproject.toml uv.lock README.md ./

# Use uv sync to install dependencies, respecting the lock file
RUN uv sync --extra app --extra dev

# Add the virtual environment's bin directory to the PATH
# This makes tools like feast and pytest available to the shell
ENV PATH="/app/.venv/bin:$PATH"

# Copy the rest of the application code
COPY . .

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
