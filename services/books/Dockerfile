ARG BUILDER_IMAGE=us-central1-docker.pkg.dev/teak-strength-485420-v3/borrow-api-repo/builder:latest
FROM ${BUILDER_IMAGE} AS builder

# Final stage
FROM python:3.11-slim

WORKDIR /app

# Copy installed dependencies from builder stage
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Use non-root user for security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
