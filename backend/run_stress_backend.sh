#!/bin/bash
# run_stress_backend.sh

# Use the seeded stress test database
export DB_PATH="stress_test.sqlite"
# Disable rate limiting during stress tests to profile the application itself
export TESTING="True"
# Use a specific folder for stress test images
export UPLOAD_FOLDER="stress_images"
mkdir -p stress_images

# Activate the venv and start the server
source .venv/bin/activate

# Use hypercorn to serve the Quart app
echo "Starting backend in stress mode on port 8000..."
# Using python3 -m hypercorn to ensure it uses the venv's version and is easier to grep
python3 -m hypercorn src.app:app --bind 0.0.0.0:8000 --access-log -
