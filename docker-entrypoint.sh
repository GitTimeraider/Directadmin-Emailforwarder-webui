#!/bin/bash
set -e

# Default to UID/GID 1000 if not set
USER_ID=${PUID:-1000}
GROUP_ID=${PGID:-1000}

echo "Starting with UID: $USER_ID, GID: $GROUP_ID"

# Create or modify the appuser with the specified IDs
# First, check if the group exists, if not create it
if ! getent group appgroup >/dev/null 2>&1; then
    groupadd -g "$GROUP_ID" appgroup
else
    # Modify existing group if needed
    groupmod -g "$GROUP_ID" appgroup 2>/dev/null || true
fi

# Check if user exists, if not create it
if ! id appuser >/dev/null 2>&1; then
    useradd -u "$USER_ID" -g appgroup -s /bin/bash -m appuser
else
    # Modify existing user
    usermod -u "$USER_ID" -g "$GROUP_ID" appuser 2>/dev/null || true
fi

# Ensure the app directory exists and set ownership
mkdir -p /app
chown -R "$USER_ID:$GROUP_ID" /app

# Create a home directory for the user if it doesn't exist
if [ ! -d "/home/appuser" ]; then
    mkdir -p /home/appuser
fi
chown -R "$USER_ID:$GROUP_ID" /home/appuser

# Export HOME for the user
export HOME=/home/appuser

# Switch to the specified user and run the command
exec gosu "$USER_ID:$GROUP_ID" "$@"
