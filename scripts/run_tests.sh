#!/bin/bash

# Research Agent Test Runner
# Properly organized test execution from scripts directory

echo "🧪 Research Agent Test Suite"
echo "============================"

# Get the project root directory (parent of scripts)
PROJECT_ROOT="$(dirname "$0")/.."
cd "$PROJECT_ROOT"

echo "📋 1. Testing Available Models..."
cd temporal-worker
uv run python ../tests/test_models_available.py
cd ..
echo ""

echo "🔬 2. Testing Research Agent Core Logic..."
cd temporal-worker
uv run python ../tests/test_research_agent.py
cd ..
echo ""

echo "✅ Test suite completed!"