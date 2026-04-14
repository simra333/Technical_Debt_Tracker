FROM python:3.10-slim

# Create non-root user 
RUN useradd -m appuser

WORKDIR /app

COPY requirements.txt .

# Create a virtual environment 
RUN python -m venv /opt/venv

# Activate virtual environment and install dependencies
RUN /opt/venv/bin/pip install -r requirements.txt

# Set environment variable to use the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

COPY . .

# Switch to non-root user
USER appuser

EXPOSE 5000

CMD ["python", "main.py"]