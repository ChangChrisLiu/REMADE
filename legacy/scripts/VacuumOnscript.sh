#!/bin/bash

# Set environment variables
export ROBOT_IP=10.125.145.89

# Run socat command
socat pty,link=/tmp/ttyUR,raw,ignoreeof,waitslave tcp:${ROBOT_IP}:54321 &
# sudo socat pty,link=/tmp/ttyUR,raw,ignoreeof,waitslave tcp:${ROBOT_IP}:54321 &

# Wait for socat to establish the connection
sleep 0.01

# Execute the demo script
python3 VacuumOn.py
sleep 0.01
pkill socat

# Run socat command
# socat pty,link=/tmp/ttyUR,raw,ignoreeof,waitslave tcp:${ROBOT_IP}:54321 &