# Neo4j GenAI OCRE

An agentic RAG (Retrieval Augmented Generation) system for exploring the Online Coins of the Roman Empire (OCRE) database using Neo4j and OpenAI. The system provides an intelligent MCP (Model Context Protocol) server that enables natural language queries about Roman coins through Claude Desktop.

## Features

- **Intelligent Tool Selection**: Automatically chooses the most appropriate search strategy based on your query
- **Multi-faceted Search**:
  - Search by emperor/authority name
  - Search by date range (with flexible BCE/CE notation)
  - Semantic search on coin descriptions, iconography, and visual features
- **Expert Context**: Provides comprehensive answers with historical context from expert numismatic knowledge
- **MCP Server Integration**: Seamlessly integrates with Claude Desktop for conversational coin exploration
- **Vision-based Identification**: Identify coins from images using GPT-4o vision (via notebooks)
- **Hybrid Retrieval**: Combines vector embeddings and full-text search for optimal results

## Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (Python package installer and environment manager)
- Neo4j database instance with OCRE data
- OpenAI API key
- Redis

You can use Docker to run Redis:
```bash
docker run --rm -p 6379:6379 redis
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd neo4j-genai-ocre
```

2. Install dependencies using uv:
```bash
uv sync
```

3. Configure environment variables:

Copy `.env.example` to `.env` and fill in your configuration:

```bash
cp .env.example .env
```

Edit `.env` with your settings:
```env
NEO4J_URI=neo4j+s://your-neo4j-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=neo4j
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536
CHAT_MODEL=gpt-4o-mini
TEMPERATURE=0.7
TOP_P=1.0
TOP_K=5
OPENAI_API_KEY=your-openai-api-key
REDIS_URL=redis://localhost:6379/0
HISTORY_LIMIT=25
```

## Running the MCP Server

### Local Development

Run the MCP server directly:

```bash
uv run mcp_server.py
```

### Integration with Claude Desktop

To use this MCP server with Claude Desktop, add the following configuration to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "roman-numismatics-assistant": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/neo4j-genai-ocre",
        "run",
        "mcp_server.py"
      ]
    }
  }
}
```

**Important**: Replace `/absolute/path/to/neo4j-genai-ocre` with the actual absolute path to your project directory.

After updating the configuration:
1. Restart Claude Desktop
2. The "roman-numismatics-assistant" server should appear in the MCP servers list
3. You can now ask Claude questions about Roman coins!

## Usage Examples

Once connected to Claude Desktop, you can ask questions like:

- "Find coins of Constantine I from the 4th century"
- "Show me coins with an emperor standing frontally holding a labarum"
- "What coins were minted between 200 and 300 CE?"
- "Find Caracalla coins with military imagery on the reverse"
- "Show me coins depicting Victory on the reverse from the 3rd century"

The system will:
1. Analyze your query
2. Automatically select the appropriate search tools (by emperor, date range, or visual features)
3. Retrieve matching coins from the Neo4j database
4. Generate a comprehensive answer with catalog references (RIC), dates, and detailed descriptions

## Project Structure

```
neo4j-genai-ocre/
├── core/
│   ├── agentic_rag_tools.py    # Search tools for different query types
│   ├── ocre_agent.py           # Agentic RAG service with tool selection
│   ├── chat.py                 # Base chat service with Jupyter UI
│   ├── models.py               # Pydantic models and settings
│   └── utils.py                # Utility functions (date parsing, Neo4j conversion)
├── notebooks/
│   ├── 1-create-knowledge-graph.ipynb  # Data ingestion and indexing
│   ├── 2-rag-chat.ipynb                # Basic RAG chat implementation
│   ├── 3-chat-history.ipynb            # Chat with Redis-backed history
│   ├── 4-agentic-rag.ipynb             # Early agentic RAG testing
│   └── 5-roman-numismatics-agent.ipynb # Full agent with vision and tools
├── data/
│   └── coins/              # Coin images for vision-based identification
├── docs/
│   └── NODES2025.pdf       # Conference presentation slides
├── mcp_server.py           # MCP server implementation
├── pyproject.toml          # Project dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## How It Works

The system uses a two-stage agentic RAG approach:

1. **Tool Selection Stage**: An LLM analyzes the user's query and selects the most appropriate search tool(s):
   - `find_coins_by_imperor`: For queries mentioning specific emperors
   - `find_coins_by_date_range`: For queries about time periods
   - `find_coins_by_free_text`: For queries about visual features and iconography

2. **Answer Generation Stage**: Retrieved coin data is formatted and passed to an expert LLM that generates a comprehensive, contextualized answer with numismatic knowledge.

The system can combine multiple search strategies for complex queries (e.g., finding coins of a specific emperor within a date range with particular iconographic features).

## Notebooks

The `notebooks/` directory contains Jupyter notebooks for exploration and development:

| Notebook | Description |
|----------|-------------|
| `1-create-knowledge-graph.ipynb` | Data ingestion pipeline - loads OCRE JSON data into Neo4j, creates embeddings, and builds indexes |
| `2-rag-chat.ipynb` | Basic RAG chat service implementation |
| `3-chat-history.ipynb` | Chat with Redis-backed conversation history |
| `4-agentic-rag.ipynb` | Early agentic RAG testing |
| `5-roman-numismatics-agent.ipynb` | Full-featured agent using OpenAI Agents SDK with vision and tools |

### Roman Numismatics Agent (Notebook 5)

The most advanced notebook implements a complete agent using the OpenAI Agents SDK with:

- **Vision Capability**: Identify coins from images using GPT-4o vision
- **Wikipedia Integration**: Enrich answers with historical context from Wikipedia
- **Hybrid Database Search**: Combine vector and full-text search for coin lookup
- **Redis Memory**: Persistent conversation history across sessions
- **Interactive UI**: Jupyter widgets for chat-based interaction

## Dependencies

Key dependencies include:
- `fastmcp`: MCP server framework
- `neo4j-graphrag[openai]`: Neo4j GraphRAG integration with OpenAI embeddings and hybrid retrieval
- `openai-agents[redis]`: OpenAI Agents SDK with Redis session memory
- `pydantic` / `pydantic-settings`: Data validation and settings management
- `python-dotenv`: Environment variable management
- `loguru`: Logging
- `pillow`: Image processing for coin vision features
- `wikipedia`: Wikipedia API client for historical context
- `ipywidgets` / `notebook`: Jupyter notebook support

See `pyproject.toml` for the complete list.

## License

See LICENSE file for details.
