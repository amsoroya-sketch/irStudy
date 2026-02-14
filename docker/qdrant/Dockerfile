# Custom Qdrant image with curl for health checks
FROM qdrant/qdrant:latest

# Install curl for health checks (run as root, default user in Qdrant base image)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Use the default entrypoint from the base image
# Note: Qdrant base image runs as root by default
