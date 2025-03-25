FROM python:3.9-slim

WORKDIR /app

# Install system libraries required by Kaleido
RUN apt-get update && apt-get install -y \
    libexpat1 \
    libxrender1 \
    libfontconfig1 \
    libxext6 \
    libx11-6 \
    libglib2.0-0 \
    git \
 && rm -rf /var/lib/apt/lists/*
 
# Create images directory
RUN mkdir -p images 

# Copy dependency file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Make entrypoint script executable
RUN chmod +x /app/entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

