# LlamaIndex Playground

LlamaIndex-based project for handling business logic with Claude AI.

## Quick Start

### 1. Activate Virtual Environment

**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Then edit `.env` and add your Anthropic API key:
```
ANTHROPIC_API_KEY=your_actual_api_key_here
```

Get your API key from: https://console.anthropic.com/

### 3. Install Dependencies

```bash
make install
```

This installs:
- **LlamaIndex** - RAG framework
- **Claude integration** - via llama-index-llms-anthropic
- **ChromaDB** - local vector database
- **HuggingFace embeddings** - free embeddings (no API key needed)
- Dev tools - black, pylint, pytest

### 4. Run Application

```bash
make run
```

### 5. See All Commands

```bash
make help
```

## Available Commands

- `make run` - Run the application
- `make test` - Run tests with coverage
- `make lint` - Code quality checks (pylint)
- `make fmt` - Format code (black)
- `make install` - Install dependencies
- `make clean` - Clean cache and storage files
- `make help` - Show all commands

## Project Structure

```
llamaindex_playground/
├── src/
│   ├── __init__.py
│   └── main.py          # Main entry point with examples
├── tests/
│   └── __init__.py
├── data/                # (Create this) Put your documents here
├── .env.example         # Environment variables template
├── .env                 # (Create this) Your actual API keys
├── requirements.txt     # Python dependencies
├── pyproject.toml       # Project configuration
├── Makefile            # Common commands
└── README.md           # This file
```

## Getting Started with LlamaIndex

### Example 1: Simple Query

```python
from llama_index.llms.anthropic import Anthropic

llm = Anthropic(api_key="your_key", model="claude-sonnet-4-5-20250929")
response = llm.complete("Explain LlamaIndex in one sentence.")
print(response)
```

### Example 2: Document Query (RAG)

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

# Load documents from data/ folder
documents = SimpleDirectoryReader("data").load_data()

# Create index
index = VectorStoreIndex.from_documents(documents)

# Query your documents
query_engine = index.as_query_engine()
response = query_engine.query("What is this document about?")
print(response)
```

### Example 3: Chat Engine

```python
# Create a chat engine for conversational queries
chat_engine = index.as_chat_engine()
response = chat_engine.chat("Tell me about the main topics")
print(response)
```

## Configuration

Edit `.env` to customize:

```bash
# Required
ANTHROPIC_API_KEY=your_key_here

# Optional - adjust chunk settings for your use case
CHUNK_SIZE=1024          # Size of text chunks for indexing
CHUNK_OVERLAP=20         # Overlap between chunks
```

## Installed Packages

**LlamaIndex:**
- `llama-index` - Main package
- `llama-index-core` - Core functionality
- `llama-index-llms-anthropic` - Claude integration
- `llama-index-embeddings-huggingface` - Free embeddings

**Storage:**
- `chromadb` - Vector database (stores locally, no server needed)

**Dev Tools:**
- `black` - Code formatter
- `pylint` - Linter
- `pytest` - Testing framework
- `pytest-cov` - Coverage reports

**Utilities:**
- `python-dotenv` - Load .env files
- `requests` - HTTP library

## Next Steps

1. **Try the examples** in `src/main.py`
2. **Add documents**: Create a `data/` folder and add .txt or .pdf files
3. **Build your logic**: Modify `src/main.py` to handle your business logic
4. **Write tests**: Add tests in `tests/` folder
5. **Explore LlamaIndex docs**: https://docs.llamaindex.ai/

## Useful Resources

- **LlamaIndex Docs**: https://docs.llamaindex.ai/
- **Claude Models**: https://docs.anthropic.com/claude/docs/models-overview
- **Example Notebooks**: https://github.com/run-llama/llama_index/tree/main/docs/examples

## Tips for Beginners

1. **Start simple**: Begin with the basic examples in `src/main.py`
2. **Test with small documents**: Use 1-2 small text files first
3. **Use ChromaDB**: It's the simplest vector store (no setup needed)
4. **Check logs**: Set `APP_DEBUG=True` in `.env` for detailed output
5. **Ask Claude**: The LLM can help explain errors and suggest fixes!

## Troubleshooting

**Import errors?**
- Make sure virtual environment is activated
- Run `make install` again

**API key errors?**
- Check `.env` file exists (copy from `.env.example`)
- Verify your API key is correct in `.env`
- **Error: "API_KEY is required in .env file"**
  - Create `.env` file from `.env.example`: `cp .env.example .env`
  - Add your API key to the `.env` file
  - Make sure `API_KEY` variable is set (not `ANTHROPIC_API_KEY`)
- **Error: "API_BASE is required in .env file"**
  - Add `API_BASE` to your `.env` file
  - Example: `API_BASE=https://api.openai.com/v1` or your custom endpoint
- **Indexing without queries?**
  - If you only need to index files (no queries), you can skip LLM validation
  - Use indexing-only mode in your code: `DocumentIndexer(require_llm=False)`

**ChromaDB errors?**
- Delete `chroma_db/` folder and try again: `make clean`

**HuggingFace download slow?**
- First run downloads embeddings model (~100MB)
- Be patient, it's a one-time download
