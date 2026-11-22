# Use lightweight official Python slim image
FROM python:3.11-slim

# Build argument to specify which microservice to package
ARG SERVICE_NAME

# Prevent Python from buffering stdout/stderr (ensures logs show immediately in K8s)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install Python dependencies first (caches layer across all 6 builds)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the target microservice's code (includes index.html for frontend-service)
COPY ${SERVICE_NAME}/ .

# Expose standard container port
EXPOSE 8000

# Run Uvicorn on 0.0.0.0 so Kubernetes/Docker can route external traffic to the container
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]