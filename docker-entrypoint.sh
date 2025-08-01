#!/bin/bash
set -e

# Default UID/GID if not provided
USER_ID=${PUID:-1000}
GROUP_ID=${PGID:-1000}

echo "Starting with UID: $USER_ID, GID: $GROUP_ID"

# Create group if it doesn't exist
if ! getent group appgroup > /dev/null 2>&1; then
    groupadd -g $GROUP_ID appgroup
fi

# Create user if it doesn't exist
if ! id -u appuser > /dev/null 2>&1; then
    useradd -u $USER_ID -g appgroup -d /app -s /bin/bash appuser
fi

# Ensure proper ownership of the app directory
chown -R appuser:appgroup /app

# Execute the main command as the appuser
exec gosu appuser "$@"
