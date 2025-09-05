FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y wget gnupg unzip curl \
    && apt-get install -y chromium chromium-driver

# Set display port to avoid crash
ENV DISPLAY=:99

# Install Python packages
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Run the bot
CMD ["python", "bot.py"]
