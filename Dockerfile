# Dockerfile for containerization
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose ports for Streamlit and Health Check Daemon
EXPOSE 8501
EXPOSE 8080

# Run main streamlit app
CMD ["streamlit", "run", "run_complete_truffle.py", "--server.port=8501", "--server.address=0.0.0.0"]
