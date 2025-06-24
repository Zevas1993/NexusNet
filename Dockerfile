# NexusNet Docker Configuration
# Multi-stage build for optimized production deployment

# Stage 1: Build environment
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Stage 2: Production environment
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    NEXUSNET_ENV=production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Create non-root user
RUN groupadd -r nexusnet && useradd -r -g nexusnet nexusnet

# Create application directory
WORKDIR /app

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/models /app/configs && \
    chown -R nexusnet:nexusnet /app

# Switch to non-root user
USER nexusnet

# Expose ports
EXPOSE 8000 8001 8002

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["python", "-m", "src.api.server"]

# Stage 3: Development environment
FROM production as development

# Switch back to root for development tools
USER root

# Install development dependencies
RUN pip install pytest pytest-cov black flake8 mypy jupyter

# Install Node.js for web UI development
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# Switch back to nexusnet user
USER nexusnet

# Override command for development
CMD ["python", "-m", "src.api.server", "--debug"]

