# =============================================================================
# Production Dockerfile for GrantLoop Backend
# Optimized for high layer cache reuse, minimal image size, and non-root runtime.
# =============================================================================

FROM python:3.12-slim

# Prevent Python from writing .pyc bytecode files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Establish primary application working directory
WORKDIR /app

# Install build tools and PostgreSQL system library headers; clean apt caches immediately
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency definition first to leverage Docker build cache on source code modifications
COPY requirements.txt /app/

# Upgrade pip and execute dependency installations without persisting build caches
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application project codebase into working directory
COPY . /app/

# Create a non-privileged dedicated system user and assign folder ownership
RUN groupadd -r django && useradd -r -g django -s /bin/false django && \
    chown -R django:django /app

# Drop root privileges and transition container runtime to dedicated non-root user
USER django

# Declare default inbound application port
EXPOSE 8000

# Launch WSGI application cluster via Gunicorn
CMD ["gunicorn", "grantloop.wsgi:application", "--bind", "0.0.0.0:8000"]
