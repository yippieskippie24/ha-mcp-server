FROM python:3.12-slim

WORKDIR /app

# Install uv for fast dependency resolution
RUN pip install --no-cache-dir uv

# Install dependencies first (layer-cached separately from source)
COPY pyproject.toml .
RUN uv pip install --system --no-cache .

# Copy application source
COPY src/ src/

EXPOSE 8080

CMD ["python", "-m", "ha_mcp"]
