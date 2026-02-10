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
├── pyproject.toml       # Project configuration (dependencies, tools)
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

---

## 🏗️ Architecture

### Design Principles

This project follows **SOLID principles** and modern software engineering practices:

- ✅ **Single Responsibility Principle** - Each class has one reason to change
- ✅ **Open/Closed Principle** - Extensible via Strategy Pattern (add languages without modifications)
- ✅ **Liskov Substitution Principle** - Abstractions are properly substitutable
- ✅ **Interface Segregation Principle** - Focused configs instead of god objects
- ✅ **Dependency Inversion Principle** - Constructor injection throughout

### Core Components

#### 1. IndexingOrchestrator (Workflow Coordinator)
**Location:** `src/indexing/indexing_orchestrator.py`
**Responsibility:** Coordinates document indexing workflow
**Coverage:** 93% (29 unit tests)

```python
orchestrator = IndexingOrchestrator(
    index_name="my_index",
    embedding_factory=embedding_factory,
    document_loader=document_loader,
    file_handler=file_handler,
    chunking_config=chunking_config,
    file_filter_config=file_filter_config,
)
orchestrator.index_directory(directory="./src", file_extensions=[".py"])
```

#### 2. Strategy Pattern for Language Support
**Location:** `src/strategies/`
**Principle:** Open/Closed - Add new languages without modifying core

**Extraction Strategies:**
- `PythonMetadataExtractor` - Extract Python classes, functions, imports
- `JavaScriptMetadataExtractor` - Extract JS/TS classes, functions
- `JavaMetadataExtractor` - Extract Java classes, methods, interfaces
- `GoMetadataExtractor` - Extract Go functions, structs

**Chunking Strategies:**
- `PythonChunker` - Smart chunking for Python code
- `JavaScriptChunker` - Smart chunking for JS/TS code
- `JavaChunker` - Smart chunking for Java code
- `GoChunker` - Smart chunking for Go code

**Adding a new language:**
```python
# 1. Create extractor: src/strategies/extraction/rust_extractor.py
class RustMetadataExtractor(LanguageMetadataExtractor):
    def extract(self, code: str) -> CodeMetadata:
        # Implementation

# 2. Create chunker: src/strategies/chunking/rust_chunker.py
class RustChunker(LanguageChunker):
    def chunk(self, code: str) -> list[CodeChunk]:
        # Implementation

# That's it! No modifications to core code needed (OCP achieved)
```

#### 3. Dependency Injection with AppFactory
**Location:** `src/app_factory.py`
**Responsibility:** Central DI wiring

```python
# Production setup
orchestrator = AppFactory.create_indexing_orchestrator(
    index_name="production_index",
    require_llm=True
)

# Test setup with mocks
orchestrator = TestAppFactory.create_test_orchestrator(
    index_name="test_index",
    embedding_factory=mock_embedding_factory,
    document_loader=mock_document_loader,
)
```

#### 4. Configuration Segregation (ISP Compliance)
**Location:** `src/config/`

Instead of one god config class, we have focused configs:

- `ChunkingConfig` - Code/doc chunking settings
- `EmbeddingConfig` - Embedding model configuration
- `ExtractionConfig` - Metadata extraction flags
- `QueryConfig` - Query engine settings
- `FileFilterConfig` - File filtering rules

Each config is a **frozen dataclass** with validation:

```python
chunking_config = ChunkingConfig.from_env()  # Load from environment
# OR
chunking_config = ChunkingConfig(
    code_chunk_size=512,
    code_chunk_overlap=50,
    doc_chunk_size=1024,
    doc_chunk_overlap=20,
    preserve_code_structure=True,
    include_line_numbers=True,
)
```

#### 5. Domain Objects (No Primitive Obsession)
**Location:** `src/domain/`

Structured data instead of primitives:

```python
# Before: tuple[str, int, int]
# After: CodeChunk (typed, validated, testable)
chunk = CodeChunk(
    content="def example(): pass",
    start_line=1,
    end_line=2,
)

# Before: dict[str, list[str]]
# After: CodeMetadata (typed, validated)
metadata = CodeMetadata(
    functions=["example", "helper"],
    classes=["MyClass"],
    imports=["os", "sys"],
)
```

### Architecture Diagram

```
AppFactory (DI Container)
    │
    ├─► IndexingOrchestrator (Coordinator)
    │       ├─► EmbeddingFactory → HuggingFaceEmbedding
    │       ├─► LLMConfigurer → CustomOpenAI
    │       ├─► DocumentLoader
    │       │       ├─► FileHandler
    │       │       └─► CodeMetadataExtractor
    │       │               └─► MetadataExtractorRegistry
    │       │                       ├─► PythonMetadataExtractor
    │       │                       ├─► JavaScriptMetadataExtractor
    │       │                       ├─► JavaMetadataExtractor
    │       │                       └─► GoMetadataExtractor
    │       └─► CodeAwareNodeParser
    │               └─► ChunkerRegistry
    │                       ├─► PythonChunker
    │                       ├─► JavaScriptChunker
    │                       ├─► JavaChunker
    │                       └─► GoChunker
    │
    └─► Configs (ISP)
            ├─► ChunkingConfig
            ├─► EmbeddingConfig
            ├─► ExtractionConfig
            ├─► QueryConfig
            └─► FileFilterConfig
```

### Refactoring Progress

**Phases Completed:**
- ✅ **Phase 1:** SOLID refactoring (configs, orchestrator, DI)
- ✅ **Phase 2:** Strategy Pattern for language support
- ✅ **Phase 3:** Test migration and coverage boost
- 🚧 **Phase 4:** Coverage boost to 80%+ (currently 52%)

**Metrics:**
- Test coverage: 12% → 52% (target: 80%+)
- Test count: 0 → 184 tests (100% passing)
- IndexingOrchestrator: 150 lines, 93% coverage
- Add new language: 2 new files, 0 modifications
- SOLID violations: All fixed ✅

## Documentation

For detailed refactoring analysis and guides, see the **[docs/](docs/)** folder:
- [docs/REFACTOR_PLAN.md](docs/REFACTOR_PLAN.md) - Full SOLID analysis
- [docs/PHASE4_PROGRESS.md](docs/PHASE4_PROGRESS.md) - Current progress tracking
- [docs/QUICKSTART.md](docs/QUICKSTART.md) - Quick start guide
- [docs/TESTING.md](docs/TESTING.md) - Testing guidelines
