#!/bin/bash

# Set environment variables
export ROBOT_IP=169.254.99.10

# Run socat command
socat pty,link=/tmp/ttyUR,raw,ignoreeof,waitslave tcp:${ROBOT_IP}:54321 &

# Wait for socat to establish the connection
sleep 0.3

# Execute the demo script
python3 VacuumOff.py