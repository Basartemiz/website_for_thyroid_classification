# Multi-stage Dockerfile for Thyroid Nodule Evaluation System
# Stage 1: Build frontend
# Stage 2: Install Python dependencies
# Stage 3: Production image

# =============================================================================
# Stage 1: Build React Frontend
# =============================================================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY frontend/ ./

# Build production bundle
RUN npm run build

# =============================================================================
# Stage 2: Install Python Dependencies
# =============================================================================
FROM python:3.11-slim AS python-builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt ./

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# =============================================================================
# Stage 3: Production Image
# =============================================================================
FROM python:3.11-slim AS production

# Labels
LABEL maintainer="Dr. Ozgur <drozgur@example.com>"
LABEL description="Thyroid Nodule Evaluation System"

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PATH="/opt/venv/bin:$PATH" \
    # Django settings
    DJANGO_SETTINGS_MODULE=config.settings.production \
    # Default port
    PORT=8000

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# Copy virtual environment from builder
COPY --from=python-builder /opt/venv /opt/venv

# Copy backend source
COPY backend/ ./

# Copy built frontend to staticfiles
COPY --from=frontend-builder /app/frontend/dist ./staticfiles/frontend

# Copy entrypoint script
COPY scripts/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Create directories for data persistence
RUN mkdir -p /data/chroma && \
    chown -R appuser:appgroup /app /data

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT:-8000}/api/health/')" || exit 1

# Entrypoint
ENTRYPOINT ["docker-entrypoint.sh"]
