# Nomic Embed Model Fix Summary

## Issue
The original configuration used `nomic-ai/nomic-embed-code-GGUF`, which is a GGUF (quantized) format model that's incompatible with the standard HuggingFace transformers library used by LlamaIndex.

## Root Cause
- GGUF models are quantized models for llama.cpp and require special loaders
- Standard HuggingFace `transformers` library doesn't recognize GGUF format
- The Nomic text embedding model requires `trust_remote_code=True` parameter
- Missing `einops` dependency required by Nomic models

## Solution

### 1. Updated Model Configuration
**Changed from:**
```
EMBED_MODEL_NAME=nomic-ai/nomic-embed-code-GGUF
```

**Changed to:**
```
EMBED_MODEL_NAME=nomic-ai/nomic-embed-text-v1.5   # 768-dim, excellent for code
EMBED_MODEL_DIMENSION=768                          # Matches model output
```

### 2. Modified Embedding Factory ([src/embedding/embedding_factory.py:45-83](src/embedding/embedding_factory.py#L45-L83))
Added support for models requiring `trust_remote_code`:

```python
# Models requiring trust_remote_code
trust_remote_models = [
    "nomic-ai/nomic-embed-text-v1.5",
    "nomic-ai/nomic-embed-text-v1",
    "nomic-ai/nomic-bert-2048"
]

# Check if model requires trust_remote_code
trust_remote_code = any(model in model_name for model in trust_remote_models)

return HuggingFaceEmbedding(
    model_name=model_name,
    device=device,
    trust_remote_code=trust_remote_code
)
```

### 3. Added Dependencies ([pyproject.toml:47-57](pyproject.toml#L47-L57))
Added `einops` to project dependencies:
```toml
dependencies = [
    ...
    "einops"  # Required for nomic-ai/nomic-embed-text-v1.5 model
]
```

### 4. Updated Tests ([tests/unit/test_embeddings_initialization.py](tests/unit/test_embeddings_initialization.py))
- Updated all HuggingFace embedding tests to expect `trust_remote_code` parameter
- Added new test `test_create_huggingface_embeddings_nomic_trust_remote_code` to verify Nomic model support

### 5. Updated Configuration Files
- Updated [.env](.env) with correct model name and dimension
- Updated [.env.example](.env.example) with comprehensive model options and notes

## Verification

### Test Results
All 13 unit tests pass:
```bash
python -m pytest tests/unit/test_embeddings_initialization.py -v
# ============================= 13 passed in 11.49s =============================
```

### Live Test
Created [test_nomic_embed.py](test_nomic_embed.py) which successfully:
- ✓ Loads the nomic-ai/nomic-embed-text-v1.5 model
- ✓ Generates 768-dimensional embeddings
- ✓ Processes code snippets in Python, JavaScript, and Java

Example output:
```
Configuration:
  Model Type: local
  Model Name: nomic-ai/nomic-embed-text-v1.5
  Device: cuda
  Dimension: 768

✓ Model created successfully!

Test 1: def hello_world():...
  ✓ Embedding shape: 768 dimensions
  ✓ Sample values: [0.0023963158, -0.0017867042, -0.1831677258, ...]
```

## Benefits

### Nomic-ai/nomic-embed-text-v1.5 Model
- **Dimensions**: 768 (vs 1024 for bge-large)
- **Parameters**: 137M (vs 335M for bge-large)
- **Performance**: Excellent for code embeddings
- **Context Length**: 8192 tokens
- **License**: Apache 2.0

### Code Changes
- Backward compatible with all existing models (BGE, MiniLM, MPNet, etc.)
- Automatic `trust_remote_code` detection
- GPU support maintained (CUDA device configuration works)
- Proper error handling and validation

## Available Models

Based on the updated [.env.example](.env.example), supported models include:

| Model | Dimensions | Parameters | Use Case |
|-------|-----------|-----------|----------|
| nomic-ai/nomic-embed-text-v1.5 | 768 | 137M | Code & text (requires einops) |
| BAAI/bge-large-en-v1.5 | 1024 | 335M | High quality general purpose |
| sentence-transformers/all-MiniLM-L6-v2 | 384 | 22M | Fast, small footprint |
| sentence-transformers/all-mpnet-base-v2 | 768 | 109M | Balanced performance |

## How to Use

1. **Install dependencies**:
   ```bash
   pip install -e .  # Installs einops and other dependencies
   ```

2. **Configure .env**:
   ```bash
   EMBED_MODEL_TYPE=local
   EMBED_MODEL_NAME=nomic-ai/nomic-embed-text-v1.5
   EMBED_DEVICE=cuda  # or cpu
   EMBED_MODEL_DIMENSION=768
   ```

3. **Run your application**:
   ```bash
   python src/main.py index /path/to/code
   ```

## Notes

- The `-GGUF` suffix indicates quantized models meant for llama.cpp, not transformers
- Standard Nomic models work out-of-the-box with the updated code
- Windows users may see symlink warnings (harmless, just a cache optimization)
- Developer mode or admin rights enable symlinks on Windows (optional)

## Files Changed
- [src/embedding/embedding_factory.py](src/embedding/embedding_factory.py) - Added trust_remote_code support
- [.env](.env) - Updated model configuration
- [.env.example](.env.example) - Added comprehensive model documentation
- [pyproject.toml](pyproject.toml) - Added einops dependency
- [tests/unit/test_embeddings_initialization.py](tests/unit/test_embeddings_initialization.py) - Updated tests
- [test_nomic_embed.py](test_nomic_embed.py) - Created verification script
