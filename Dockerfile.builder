# Shared Builder Image
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

# Install dependencies into a specific location that can be copied later
# We use /install as the prefix
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
