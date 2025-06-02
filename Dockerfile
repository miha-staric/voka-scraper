# Use a lightweight Python 3 base image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements first (to leverage Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY voka.py config.toml ./

# Set default command
CMD ["python", "voka.py"]
