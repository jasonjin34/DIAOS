# Next.js Client Dockerfile with bun package manager

FROM oven/bun:1 AS base

# Install system dependencies including Python for native modules
RUN apt-get update && apt-get install -y \
    curl \
    python3 \
    python3-pip \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json bun.lock* ./

# Install dependencies
RUN bun install --frozen-lockfile

# Copy source code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash nextjs
RUN chown -R nextjs:nextjs /app
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
  CMD curl --fail http://localhost:3000/api/health || exit 1

# Start the development server
CMD ["bun", "dev"]