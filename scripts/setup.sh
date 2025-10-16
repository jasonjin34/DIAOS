#!/bin/bash

# Research Agent Development Setup Script

set -e

echo "🔬 Academic Research Agent Setup"
echo "================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Navigate to project root from scripts directory
cd "$(dirname "$0")/.."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API key before continuing!"
    echo "   Required: OPENAI_API_KEY"
    exit 1
fi

# Validate API keys
if ! grep -q "your_.*_api_key_here" .env; then
    echo "✅ Environment file configured"
else
    echo "⚠️  Please set your API key in .env file!"
    echo "   Required: OPENAI_API_KEY"
    exit 1
fi

echo "🚀 Starting services with Docker Compose..."

# Start services
docker-compose up -d

echo "⏳ Waiting for services to be ready..."

# Wait for Temporal server
echo "   Waiting for Temporal server..."
timeout=60
while [ $timeout -gt 0 ]; do
    if curl -f http://localhost:7233/api/v1/namespaces > /dev/null 2>&1; then
        break
    fi
    sleep 2
    timeout=$((timeout - 2))
done

if [ $timeout -le 0 ]; then
    echo "❌ Temporal server failed to start"
    exit 1
fi

# Wait for Next.js client
echo "   Waiting for Next.js client..."
timeout=60
while [ $timeout -gt 0 ]; do
    if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
        break
    fi
    sleep 2
    timeout=$((timeout - 2))
done

if [ $timeout -le 0 ]; then
    echo "❌ Next.js client failed to start"
    exit 1
fi

echo ""
echo "✅ All services are running!"
echo ""
echo "🌐 Access URLs:"
echo "   Research Dashboard: http://localhost:3000"
echo "   Temporal Web UI:    http://localhost:8080"
echo ""
echo "📋 Useful Commands:"
echo "   View logs:          docker-compose logs -f"
echo "   Stop services:      docker-compose down"
echo "   Restart services:   docker-compose restart"
echo ""
echo "🔬 Ready to start researching!"