# ==========================================
# Stage 1: Build dependencies in virtual env
# ==========================================
FROM python:3.10-slim AS builder

WORKDIR /app

# Prevent python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment to isolate dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install python dependencies
# Using PyTorch CPU wheels to minimize image size (~1.5GB vs ~5GB)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu --extra-index-url https://pypi.org/simple -r requirements.txt

# ==========================================
# Stage 2: Final lightweight runner image
# ==========================================
FROM python:3.10-slim AS runner

WORKDIR /app

# Prevent python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install runtime system dependencies for OpenCV, FFMPEG, and Tesseract-OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment containing installed python packages from the builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create a non-root system user and group for enhanced runtime security
RUN groupadd -g 1000 appgroup && \
    useradd -r -u 1000 -g appgroup -d /app -s /sbin/nologin appuser

# Pre-create writable directories for the application and adjust ownership
RUN mkdir -p static/audio templates

# Copy application source code
COPY . .

# Set ownership of all application files and venv to the non-root user
RUN chown -R appuser:appgroup /app /opt/venv

# Switch to the non-root user
USER appuser

# Expose FastAPI application port
EXPOSE 8000

# Default Gunicorn entrypoint command with Uvicorn workers
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "server:app"]
