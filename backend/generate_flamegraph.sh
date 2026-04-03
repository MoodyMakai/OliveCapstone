#!/bin/bash
# generate_flamegraph.sh

# Use lsof to find the PID of the process listening on port 8000 (most reliable)
# We use head -n 1 in case there are multiple PIDs (e.g., workers)
PID=$(lsof -ti:8000 | head -n 1)

if [ -z "$PID" ]; then
    echo "Error: No process found listening on port 8000."
    echo "Make sure the backend is running (run ./run_stress_backend.sh)."
    exit 1
fi

echo "Found backend process with PID: $PID"

# Check if DevToolsSecurity is enabled (common macOS hurdle for py-spy)
if command -v DevToolsSecurity >/dev/null 2>&1; then
    STATUS=$(DevToolsSecurity -status)
    if [[ "$STATUS" == *"disabled"* ]]; then
        echo "Warning: DevToolsSecurity is disabled. This often causes py-spy timeouts on macOS."
        echo "Try running: sudo DevToolsSecurity -enable"
    fi
fi

echo "Capturing flamegraph for 60 seconds..."
source .venv/bin/activate

# Use a lower sampling rate and include idle time to avoid kernel timeouts (os error 60)
# Note: On macOS, py-spy ALMOST ALWAYS requires sudo.
echo "------------------------------------------------------------------"
echo "CRITICAL: If you get 'os error 60' or 'Permission denied', you MUST run:"
echo "sudo .venv/bin/py-spy record --idle --rate 100 -o profile.svg --pid $PID --duration 60"
echo "------------------------------------------------------------------"

py-spy record --idle --rate 100 -o profile.svg --pid "$PID" --duration 60
echo "Flamegraph saved to profile.svg"
