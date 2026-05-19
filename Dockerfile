# Use stable Python image
FROM python:3.11-slim

# Avoid prompts during package install
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install required system packages
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    build-essential \
    libglib2.0-0 \
    libnss3 \
    libfontconfig1 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxi6 \
    libxtst6 \
    libatk1.0-0 \
    libgtk-3-0 \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependency files first (for Docker cache)
COPY requirements.txt .
COPY setup.py .

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install -r requirements.txt

# Install spaCy language model
RUN python -m spacy download en_core_web_sm

# Copy full project
COPY . .

# Install package
RUN pip install -e .

# Create output folders
RUN mkdir -p \
    job_apply_ai/outputs/jobs \
    job_apply_ai/outputs/cvs

# Environment variables for Selenium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Expose web UI port
EXPOSE 5000

# Start application
CMD ["job-apply-ai", "web"]
