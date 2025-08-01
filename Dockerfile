FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create directories for templates and static files
RUN mkdir -p templates static

EXPOSE 5000

CMD ["python", "app.py"]
