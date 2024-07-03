# Use the official Python 3.12 image as the base image
FROM python:3.12-slim

ENV LISTEN_PORT=5000
EXPOSE 5000

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    mariadb-client \
    pkg-config \
    librdkafka-dev \
    git

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed dependencies specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install kafka-python directly from GitHub repository
RUN pip install --no-cache-dir git+https://github.com/dpkp/kafka-python.git

# Run app.py when the container launches
CMD ["python", "app.py"]