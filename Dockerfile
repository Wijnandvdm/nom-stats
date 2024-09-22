FROM python:3.9-alpine

# Install necessary dependencies for PyYAML
RUN apk update && apk add --no-cache gcc musl-dev libffi-dev

WORKDIR /app

COPY . /app

# Install the Python dependencies (no cache to reduce image size)
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]
