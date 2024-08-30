# Use the official Python 3.9 Alpine image
FROM python:3.9-alpine

# Install dependencies for PyYAML
RUN apk update && apk add --no-cache gcc musl-dev libffi-dev

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the script
CMD ["python", "app.py"]
