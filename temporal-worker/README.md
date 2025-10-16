# Temporal Worker - Research Agent

A durable AI research agent built with Temporal workflows for paper discovery, analysis, and research automation.

## Features

- **Enhanced ArXiv Integration**: Uses arxiv-mcp-server for optimized paper search and retrieval
- **Local Paper Storage**: Automatic caching and local storage of downloaded papers
- **Citation Analysis**: Extract and analyze citation networks from research papers
- **Semantic Search**: Find similar papers using semantic similarity
- **PDF Processing**: Extract and process text content from academic papers
- **Temporal Workflows**: Durable, fault-tolerant research workflows

## ArXiv MCP Server Integration

This project integrates with [arxiv-mcp-server](https://pypi.org/project/arxiv-mcp-server/) to provide enhanced arXiv paper search and management capabilities.

### Installation

First, install the arxiv-mcp-server tool:

```bash
uv tool install arxiv-mcp-server
```

### MCP Server Usage

The arxiv-mcp-server provides these tools through the Model Context Protocol (MCP):

- **search_papers**: Advanced paper search with category filtering and date ranges
- **download_paper**: Download papers with automatic PDF conversion
- **list_papers**: List all locally stored papers
- **read_paper**: Read stored papers in markdown format

### Search Capabilities

The MCP server supports advanced search syntax:

```python
# Title-specific search
query = 'ti:"Deep Residual Learning for Image Recognition"'

# Category filtering
categories = ["cs.CV", "cs.LG"]  # Computer Vision & Machine Learning

# Date filtering
date_from = "2020-01-01"  # Papers from 2020 onwards
```

### Demo Results

Successfully demonstrated retrieval of the ResNet paper:

- **Paper**: "Deep Residual Learning for Image Recognition"
- **Authors**: Kaiming He, Xiangyu Zhang, Shaoqing Ren, Jian Sun
- **ArXiv ID**: 1512.03385v1
- **Status**: Successfully searched and downloaded via MCP server

### MCP Protocol Implementation

The integration uses JSON-RPC 2.0 for communication:

1. **Initialize**: Start MCP server with protocol version 2024-11-05
2. **Notify**: Send `notifications/initialized` after initialization
3. **Discover**: Use `tools/list` to discover available tools
4. **Execute**: Use `tools/call` to execute specific tool functions

## Installation

```bash
# Install dependencies
uv sync

# Install arxiv-mcp-server (required for arXiv functionality)
uv tool install arxiv-mcp-server

# Verify installation
uv tool list | grep arxiv-mcp-server
```

### Prerequisites

- **uv**: Modern Python package manager ([install uv](https://github.com/astral-sh/uv))
- **arxiv-mcp-server**: Model Context Protocol server for arXiv ([PyPI](https://pypi.org/project/arxiv-mcp-server/))
- **Temporal Server**: For workflow orchestration

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test categories
uv run pytest -m unit          # Unit tests
uv run pytest -m integration   # Integration tests
uv run pytest -m arxiv         # ArXiv API tests
```

### Test Markers

- `unit`: Fast, isolated unit tests
- `integration`: Integration tests with real APIs
- `arxiv`: Tests requiring arXiv API access
- `openai`: Tests requiring OpenAI API
- `temporal`: Tests requiring Temporal server

## Architecture

### Core Components

- **Activities**: Tool execution and LLM interactions
- **Workflows**: Research orchestration and state management
- **Tools**: Paper discovery, analysis, and processing utilities
- **Registry**: Dynamic tool discovery and validation

### Tool Registry

The system provides these research tools:

- `arxiv_search_papers`: Enhanced search with MCP server
- `arxiv_download_paper`: Download with local storage
- `arxiv_list_papers`: List downloaded papers
- `arxiv_read_paper`: Read stored paper content
- `arxiv_get_metadata`: Get enhanced paper metadata
- `arxiv_deep_analysis`: Comprehensive paper analysis with executive summary
- `extract_citations`: Citation extraction and parsing
- `analyze_citation_network`: Citation network analysis
- `process_pdf`: PDF text extraction
- `extract_sections`: Academic paper section extraction
- `find_similar_papers`: Semantic similarity search
- `calculate_similarity`: Similarity calculation

## Configuration

### Environment Variables

```bash
# ArXiv storage location
ARXIV_STORAGE_PATH=./arxiv_papers

# OpenAI API key (for LLM activities)
OPENAI_API_KEY=your_key_here

# Temporal server configuration
TEMPORAL_HOST=localhost:7233
```

### Storage Structure

```
arxiv_papers/
├── papers_index.json          # Local paper index
├── 1512.03385v1.pdf          # Downloaded papers
├── 1512.03385v1_metadata.json # Paper metadata
└── ...
```

## ArXiv MCP Server Details

### Technical Implementation

The arxiv-mcp-server integration demonstrates:

- **Real-time Communication**: JSON-RPC over stdio
- **Advanced Search**: Field-specific queries and category filtering
- **Local Storage**: Automatic paper caching and indexing
- **Metadata Management**: Rich paper metadata with local storage status

### Successful Integration Points

1. **Initialization Sequence**: Proper MCP protocol handshake
2. **Tool Discovery**: Runtime discovery of server capabilities
3. **Paper Search**: Advanced query syntax with category filtering
4. **Paper Retrieval**: Download and local storage management
5. **Error Handling**: Comprehensive error handling and cleanup

### Future Enhancements

- Integration of MCP client into Temporal activities
- Semantic search on locally stored papers
- Citation network analysis with downloaded papers
- Research workflow automation with enhanced arXiv capabilities

## License

MIT License - see LICENSE file for details.