# Academic Research Agent

A durable AI research agent built with Temporal workflows and Next.js, designed for deep academic paper discovery, citation analysis, and idea validation using arXiv and other academic sources.

## Architecture

### 🐍 Python Temporal Worker
- **Research Workflows**: Orchestrates multi-step research processes
- **Dynamic Tool Execution**: Runtime tool selection based on research needs
- **arXiv Integration**: Comprehensive paper discovery and metadata extraction
- **Citation Analysis**: Reference network mapping and relationship discovery
- **PDF Processing**: Full-text extraction and section analysis
- **LLM Decision Making**: Intelligent research strategy and tool selection

### ⚛️ Next.js Client
- **Interactive Dashboard**: Modern research interface with real-time updates
- **Workflow Management**: Start, monitor, and control research sessions
- **Progress Streaming**: Live updates using Server-Sent Events
- **Result Visualization**: Comprehensive research result presentation
- **AI SDK Integration**: Streaming interface for research progress

## Technology Stack

- **Backend**: Python 3.11+ with uv package manager
- **Frontend**: Next.js 15 with bun package manager, AI SDK integration
- **Orchestration**: Temporal workflows for durability and reliability
- **Database**: PostgreSQL for workflow persistence and chat history
- **Authentication**: NextAuth.js with multiple provider support
- **Containerization**: Docker Compose for local development
- **AI/LLM**: OpenAI GPT-4 integration with streaming responses
- **Additional Services**: Redis for caching and session storage

## Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key

### 1. Clone and Setup

```bash
git clone <repository-url>
cd temporal-agent-tutorial

# Copy environment template
cp .env.example .env

# Edit .env with your API key
# Required: OPENAI_API_KEY
```

### 2. Start with Docker Compose

```bash
# Using setup script (recommended)
./scripts/setup.sh

# Or manually
docker-compose up -d

# View logs
docker-compose logs -f

# Check service health
docker-compose ps
```

### 3. Access the Application

- **AI Chat Interface**: http://localhost:3000
- **Temporal Web UI**: http://localhost:8080
- **PostgreSQL**: localhost:5432 (temporal/temporal)
- **Redis**: localhost:6379

### 4. Run Tests

```bash
# Run all tests
./scripts/run_tests.sh

# Run worker tests specifically
cd temporal-worker
uv run pytest tests/

# Run client tests
cd temporal-client
bun test
```

## Development Setup

### Manual Development (Alternative to Docker)

#### Python Worker Setup

```bash
cd temporal-worker

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Start worker
uv run python -m src.worker
```

#### Next.js Client Setup

```bash
cd temporal-client

# Install bun (if not already installed)
curl -fsSL https://bun.sh/install | bash

# Install dependencies
bun install

# Run database migrations
bun run db:migrate

# Start development server
bun dev
```

#### Start Temporal Server

```bash
# Option 1: Using Docker
docker run --rm -p 7233:7233 temporalio/auto-setup:latest

# Option 2: Local installation
temporal server start-dev
```

## Usage

### AI Chat Interface

1. Navigate to http://localhost:3000
2. Sign in or continue as guest
3. Start a conversation with the AI assistant
4. Ask research questions or request academic analysis
5. The system will automatically:
   - Route complex research queries to Temporal workflows
   - Search arXiv for relevant papers via MCP tools
   - Analyze citations and relationships
   - Process paper content and provide summaries
   - Generate artifacts and interactive content

### Core Features

- **Conversational AI**: Natural language research assistance with streaming responses
- **Paper Discovery**: Intelligent arXiv search with MCP integration
- **Citation Analysis**: Reference network mapping and relationship discovery
- **PDF Processing**: Full-text content extraction and semantic analysis
- **Artifact Generation**: Interactive documents, code, and visualizations
- **Authentication**: Secure user sessions with NextAuth.js
- **Chat History**: Persistent conversation storage with PostgreSQL

### Temporal Integration

- **Durable Workflows**: Research processes continue even if interrupted
- **Tool Registry**: Dynamic tool selection and validation
- **Activity Patterns**: Retry policies and error handling
- **Workflow Monitoring**: Real-time status via Temporal Web UI

## API Reference

### Core Endpoints

- `POST /api/chat` - Main chat interface with AI SDK streaming
- `GET /api/chat/[id]` - Get specific chat conversation
- `POST /api/research/poll/[workflowId]` - Poll Temporal workflow status
- `GET /api/auth/*` - NextAuth.js authentication endpoints
- `POST /api/files/upload` - File upload for document analysis

### Chat Integration Example

```javascript
import { useChat } from 'ai/react';

export default function ChatComponent() {
  const { messages, input, handleInputChange, handleSubmit } = useChat();
  
  return (
    <div>
      {messages.map(m => (
        <div key={m.id}>
          {m.role}: {m.content}
        </div>
      ))}
      
      <form onSubmit={handleSubmit}>
        <input
          value={input}
          onChange={handleInputChange}
          placeholder="Ask about research..."
        />
      </form>
    </div>
  );
}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `TEMPORAL_SERVER_ADDRESS` | Temporal server address | localhost:7233 |
| `TEMPORAL_NAMESPACE` | Temporal namespace | default |
| `TEMPORAL_TASK_QUEUE` | Task queue name | research-agent-queue |
| `POSTGRES_URL` | PostgreSQL connection string | postgres://temporal:temporal@localhost:5432/temporal |
| `REDIS_URL` | Redis connection string | redis://localhost:6379 |
| `NODE_ENV` | Node environment | development |

### Built-in Tools

The system includes the following research tools in `temporal-worker/src/tools/`:

- **arXiv Client (MCP)**: Paper discovery with MCP integration
- **Citation Analyzer**: Reference parsing and network analysis
- **PDF Processor**: Full-text content extraction using pdfplumber
- **Semantic Search**: AI-powered similarity matching
- **Tool Registry**: Dynamic tool management and validation

## Development

### Project Structure

```
temporal-agent-tutorial/
├── temporal-worker/          # Python Temporal worker
│   ├── src/
│   │   ├── activities/       # Temporal activities
│   │   ├── workflows/        # Temporal workflows
│   │   ├── tools/           # Research tools (MCP, arXiv, PDF)
│   │   └── config/          # Configuration
│   ├── tests/               # Unit tests
│   └── scripts/             # Test and verification scripts
├── temporal-client/         # Next.js AI chat client
│   ├── app/                 # App Router pages and API
│   ├── components/          # React components
│   ├── lib/                 # Utilities and database
│   └── hooks/               # Custom React hooks
└── scripts/                 # Project-level scripts
```

### Adding New Tools

1. Create tool in `temporal-worker/src/tools/`
2. Register in `temporal-worker/src/tools/registry.py`
3. Add activity wrapper if needed
4. Test with `uv run pytest tests/unit/tools/`

### Extending Chat Features

1. Add components in `temporal-client/components/`
2. Create API routes in `temporal-client/app/api/`
3. Add database models in `temporal-client/lib/db/schema.ts`
4. Use hooks for state management

## Troubleshooting

### Common Issues

1. **Worker not connecting**: Check Temporal server is running
2. **API key errors**: Verify environment variables are set
3. **Port conflicts**: Ensure ports 3000, 7233, 8080 are available
4. **Docker issues**: Check `docker-compose logs` for details

### Debugging

- Temporal Web UI: http://localhost:8080 for workflow inspection
- Worker logs: `docker-compose logs temporal-worker`
- Client logs: `docker-compose logs temporal-client`

### Performance Tuning

- Adjust `max_iterations` in research workflow
- Configure tool timeout values
- Optimize PDF processing batch sizes

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request with description

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Check existing issues in repository
- Create new issue with detailed description
- Include logs and environment details