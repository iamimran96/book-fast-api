FROM python:3.12-slim AS build

# Install dependencies
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

# Install system-wide so binaries go to /usr/local/bin (world-executable)
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim AS api-prod

# Set working directory
WORKDIR /opt/project

# Bring installed packages & console scripts (incl. uvicorn) from build
COPY --from=build /usr/local /usr/local

# Copy application code
COPY ./ ./

# Set PYTHONPATH
ENV PYTHONPATH=/opt/project

# Set default port via environment variable
ENV PORT=8080

# TODO: Set the default command with dynamic worker calculation using 2 * CPU_COUNT for I/O-bound applications
CMD ["/bin/sh", "-c", "if [ \"$(alembic current)\" != \"$(alembic heads)\" ]; then alembic upgrade head; else echo 'Migrations are up-to-date.'; fi && uvicorn  src:app --workers 4 --host 0.0.0.0 --port ${PORT}"]
