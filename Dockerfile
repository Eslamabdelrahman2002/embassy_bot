FROM python:3.10-slim

# Install system dependencies needed for Chrome and Selenium
RUN apt-get update && apt-get install -y wget gnupg unzip \
    && apt-get install -y chromium chromium-driver

# Set up a working directory
WORKDIR /app

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files
COPY . .

# Run the bot
CMD ["python", "embassy_bot.py"]
