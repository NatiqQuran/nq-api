FROM python:3.13-slim AS builder

# Create the app directory
RUN mkdir /app

# Set the working directory
WORKDIR /app

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

# Upgrade pip and install dependencies
RUN pip install --upgrade pip 

# Copy the requirements file first (better caching)
COPY requirements.txt /app/

RUN apt update \
    && apt -y install libpq-dev gcc

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production stage
FROM python:3.13-slim

RUN useradd -m -r appuser && \
    mkdir /app && \
    chown -R appuser /app

# Copy the Python dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

RUN apt-get update \
    && apt-get -y install libpq-dev gcc libmagic1

# Set the working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser . .

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

RUN mkdir /app/staticfiles
RUN chown appuser:appuser /app/staticfiles

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 8000 

RUN chmod +x /app/entrypoint.prod.sh

ENTRYPOINT ["/app/entrypoint.prod.sh"]