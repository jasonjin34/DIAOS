#!/bin/bash
# Test execution script for research agent

set -e

echo "🧪 Research Agent Test Suite"
echo "============================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to run command with status
run_test() {
    local name="$1"
    local cmd="$2"
    
    echo -e "\n${BLUE}📋 $name${NC}"
    echo "Command: $cmd"
    
    if eval "$cmd"; then
        echo -e "${GREEN}✅ $name passed${NC}"
        return 0
    else
        echo -e "${RED}❌ $name failed${NC}"
        return 1
    fi
}

# Check if we're in the right directory
if [[ ! -f "pyproject.toml" ]]; then
    echo -e "${RED}❌ Error: Run this script from the temporal-worker directory${NC}"
    exit 1
fi

# Install test dependencies
echo -e "${YELLOW}📦 Installing test dependencies...${NC}"
uv sync --extra test

# Run different test suites based on arguments
case "${1:-fast}" in
    "unit")
        echo -e "\n${BLUE}🏃 Running Unit Tests Only${NC}"
        run_test "Unit Tests" "uv run pytest tests/unit/ -v -m unit"
        ;;
        
    "integration")
        echo -e "\n${BLUE}🌐 Running Integration Tests Only${NC}"
        run_test "Integration Tests" "uv run pytest tests/integration/ -v -m integration"
        ;;
        
    "fast")
        echo -e "\n${BLUE}⚡ Running Fast Tests Only${NC}"
        run_test "Fast Tests" "uv run pytest -v -m 'not slow and not temporal'"
        ;;
        
    "coverage")
        echo -e "\n${BLUE}📊 Running Tests with Coverage${NC}"
        run_test "Coverage Tests" "uv run pytest --cov=src --cov-report=term-missing --cov-report=html:htmlcov --cov-fail-under=70"
        echo -e "${GREEN}📋 Coverage report: file://$(pwd)/htmlcov/index.html${NC}"
        ;;
        
    "help"|"--help"|"-h")
        echo "Usage: $0 [test-type]"
        echo ""
        echo "Test Types:"
        echo "  unit        - Run unit tests only (fast, mocked)"
        echo "  integration - Run integration tests only (real APIs)"
        echo "  fast        - Run all tests except slow/temporal ones (default)"
        echo "  coverage    - Run tests with coverage reporting"
        echo "  help        - Show this help"
        echo ""
        echo "Examples:"
        echo "  $0 unit           # Fast unit tests"
        echo "  $0 integration    # Integration tests with real APIs"
        echo "  $0 coverage       # Tests with coverage report"
        echo ""
        ;;
        
    *)
        echo -e "${RED}❌ Unknown test type: $1${NC}"
        echo "Run '$0 help' for usage information"
        exit 1
        ;;
esac

echo -e "\n${GREEN}🎉 Test execution completed!${NC}"