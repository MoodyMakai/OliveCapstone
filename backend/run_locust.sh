#!/bin/bash
# run_locust.sh
source .venv/bin/activate
echo "Starting Locust load test on http://localhost:8000..."
locust -f locustfile.py --host http://localhost:8000
