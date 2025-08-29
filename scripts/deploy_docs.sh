#!/bin/bash
set -e

# Ensure we are at the project root
if [ ! -f "mkdocs.yml" ]; then
    echo "This script must be run from the project root."
    exit 1
fi

# Get the remote URL
REMOTE_URL=$(git config --get remote.origin.url)
if [ -z "$REMOTE_URL" ]; then
    echo "Could not get remote URL. Are you in a git repository?"
    exit 1
fi

echo "Building documentation..."
uv run mkdocs build

echo "Preparing for deployment..."
# Create a temporary directory for deployment
DEPLOY_DIR=$(mktemp -d)

# Copy the built site to the deployment directory
cp -r site/* "$DEPLOY_DIR"

# Go into the deployment directory
cd "$DEPLOY_DIR"

# Initialize a new git repository
git init
git add .
git commit -m "Deploy documentation from $(date)"

echo "Deploying to gh-pages branch..."
# Push to the gh-pages branch of the original repository
git push --force "$REMOTE_URL" master:gh-pages

# Go back to the original directory and clean up
cd - > /dev/null
rm -rf "$DEPLOY_DIR"

echo "Documentation deployed successfully."
