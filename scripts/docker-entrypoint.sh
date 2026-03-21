#!/bin/bash
set -e

# Remove any stale lock files
rm -f /tmp/.X99-lock

# Start Xvfb in the background to provide a virtual display for Playwright
# This allows running in "headed" mode (passing bot detection) while in a container.
Xvfb :99 -screen 0 1280x720x24 &
export DISPLAY=:99

# Wait for Xvfb to start
sleep 2

# Execute the command passed to the container
exec "$@"
