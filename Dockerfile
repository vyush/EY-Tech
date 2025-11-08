# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY loan_agent_complete.py .
COPY .env.example .

# Create .env file from example
RUN cp .env.example .env

# Expose the port Gradio uses
EXPOSE 7861

# Set environment variables
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7861

# Run the application
CMD ["python", "loan_agent_complete.py"]