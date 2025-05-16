FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Install the package in development mode
RUN pip install -e .

# Set the entrypoint to run the CLI
ENTRYPOINT ["league-ranker"]

# Display help message by default
CMD ["--help"]