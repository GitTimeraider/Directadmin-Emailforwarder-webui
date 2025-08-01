FROM python:3.9-slim

# Install gosu for proper user switching
RUN apt-get update && apt-get install -y \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Create app directory with proper permissions
RUN mkdir -p /app && chmod 755 /app

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY templates templates/
COPY static static/

# Create a non-root user that will be modified by entrypoint
RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -s /bin/bash -m appuser

# Copy entrypoint script and make it executable
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# Set ownership of app directory to root initially
# The entrypoint will change this based on PUID/PGID
RUN chown -R root:root /app && \
    chmod -R 755 /app && \
    chmod -R 644 /app/* && \
    find /app -type d -exec chmod 755 {} \;

EXPOSE 5000

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "4", "--worker-class", "gthread", "app:app"]
