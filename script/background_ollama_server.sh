#!/bin/bash
pgrep -f ollama | grep -v $$ | xargs -r kill
# kill all ollama processes expect the current one (this one)

ollama serve 2>&1 | tee ollama.server.log &
# Store the process ID (PID) of the background command

check_server_is_running() {
    # Check for "warning: gpu support" or "Listening" in the log file
    if tail -n 1 ollama.server.log | grep -Eq "warning: gpu support|Listening"; then
        return 0 # Success
    else
        return 1 # Failure
    fi
}

# Wait for the process to print "Listening"
while ! check_server_is_running; do
    echo "waiting for ollama server to start..."
    sleep 1
done