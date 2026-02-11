# Empty Response Issue - Root Cause Analysis and Fix

**Date:** 2026-02-12
**Issue:** Query engine returning "Empty Response" instead of actual LLM answers
**Status:** ✅ RESOLVED

---

## Problem Description

When querying the indexed codebase, the system was returning literal text "Empty Response" (14 characters) instead of the actual Claude AI response. This affected both `main.py` and `quick_test.py`.

### Symptoms
- LLM was configured correctly (verified with direct `Settings.llm.complete()` calls)
- Document retrieval was working (nodes were retrieved successfully)
- But query engine returned: `"Empty Response"`

---

## Root Cause Analysis

### Root Cause #1: Invalid Model Name ❌

**File:** `.env` line 4

**Problem:**
```env
MODEL_NAME=claude-sonnet-4-5-20250929  # ❌ Invalid model ID
```

**Evidence:**
```bash
# API Error:
{
  "error": {
    "message": "Invalid model name passed in model=claude-sonnet-4-5-20250929.
                Call `/v1/models` to view available models for your key."
  }
}
```

**Fix:**
```env
MODEL_NAME=claude-sonnet-4-5  # ✅ Valid model ID
```

**Available Models on Endpoint:**
- `claude-sonnet-4-5` ✅
- `claude-opus-4-6`
- `claude-haiku-4-5`
- `gpt-4`, `gpt-4o`, `gpt-5`
- Many more...

---

### Root Cause #2: LlamaIndex Response Synthesizer Bug 🐛

**File:** `src/code_query_engine.py`

**Problem:**

LlamaIndex's `get_response_synthesizer()` was incompatible with custom OpenAI endpoints, returning "Empty Response" even when:
- Direct LLM calls worked: `Settings.llm.complete("test")` → ✅ "Hello World"
- Retrieval worked: `retriever.retrieve(query)` → ✅ Retrieved 3 nodes
- But query engine failed: `query_engine.query("test")` → ❌ "Empty Response"

**Original Code (Broken):**
```python
from llama_index.core.response_synthesizers import get_response_synthesizer

response_synthesizer = get_response_synthesizer(
    response_mode="compact",
    text_qa_template=qa_prompt_template,
)

query_engine = RetrieverQueryEngine(
    retriever=retriever,
    response_synthesizer=response_synthesizer,  # ❌ Returns "Empty Response"
)
```

**Tested Modes (All Failed):**
- `response_mode="compact"` → "Empty Response"
- `response_mode="tree_summarize"` → "Empty Response"
- `response_mode="simple_summarize"` → "Empty Response"
- `response_mode="refine"` → "Empty Response"

**Root Issue:**

The `get_response_synthesizer()` factory has internal compatibility issues with custom OpenAI-compatible endpoints. It appears to fail silently and return the default "Empty Response" fallback.

---

## Solution

### Implemented Custom Query Engine

**File:** `src/code_query_engine.py`

**Strategy:** Bypass `get_response_synthesizer()` entirely and manually handle the RAG pipeline.

**New Architecture:**

```python
class CustomQueryEngine:
    """Manual RAG pipeline that bypasses LlamaIndex's buggy synthesizer."""

    def query(self, query_str: str) -> Response:
        # 1. Retrieve documents
        nodes = self.retriever.retrieve(QueryBundle(query_str=query_str))

        # 2. Build context string manually
        context_parts = [node.text for node in nodes]
        context_str = "\n\n".join(context_parts)

        # 3. Build prompt manually
        prompt = self.prompt_template.format(
            context_str=context_str,
            query_str=query_str
        )

        # 4. Call LLM directly (bypassing synthesizer)
        llm_response = Settings.llm.complete(prompt)

        # 5. Create Response object manually
        return Response(
            response=llm_response.text,
            source_nodes=nodes,
            metadata={"query_str": query_str}
        )
```

**Key Changes:**

1. **Direct LLM Call**: Uses `Settings.llm.complete()` directly instead of synthesizer
2. **Manual Context Building**: Constructs context from retrieved nodes manually
3. **Manual Prompt Formatting**: Uses string `.format()` instead of `PromptTemplate`
4. **Manual Response Object**: Creates `Response` object directly

**Result:** ✅ Works perfectly with custom endpoints!

---

### Root Cause #3: Windows Console Encoding 🪟

**File:** `quick_test.py`

**Problem:**
```python
print("用繁體中文介紹這個代碼庫：")
# UnicodeEncodeError: 'charmap' codec can't encode characters
```

**Fix:**
```python
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

---

## Files Modified

### Core Fixes
1. **`.env`** - Changed model name from `claude-sonnet-4-5-20250929` to `claude-sonnet-4-5`
2. **`src/code_query_engine.py`** - Implemented `CustomQueryEngine` class
3. **`src/llm/llm_configurer.py`** - Added `max_tokens=4096` parameter
4. **`quick_test.py`** - Added Windows UTF-8 encoding fix

### No Changes Needed
- `src/indexing/indexing_orchestrator.py` - Already worked correctly
- `src/app_factory.py` - Already worked correctly
- All other core files - Already worked correctly

---

## Verification

### Test 1: Direct LLM Call ✅
```python
Settings.llm.complete("Say hello")
# Output: "Hello! How can I help you today?"
```

### Test 2: Manual Query ✅
```python
orchestrator.query("introduce repo by traditional chinese", top_k=5)
# Output: "這個專案是一個基於 Go 語言開發的 AI 模型服務處理器..."
# (Full Traditional Chinese response)
```

### Test 3: Main Application ✅
```bash
python src/main.py
# Queries work correctly with proper responses
```

---

## Lessons Learned

### 1. **Always Test with Direct API Calls First**
When debugging LLM integration issues:
1. Test direct API with `curl` or `requests`
2. Test LlamaIndex LLM wrapper with `.complete()`
3. Test retrieval separately
4. Then test query engine

This isolates where the problem actually is.

### 2. **LlamaIndex Abstractions Can Hide Issues**
High-level abstractions like `get_response_synthesizer()` can fail silently with custom endpoints. When in doubt, implement the logic manually.

### 3. **Verify Model Names Against Actual API**
Always check `/v1/models` endpoint to see what's actually available. Don't assume model naming conventions.

### 4. **Custom OpenAI Endpoints Need Special Handling**
Not all OpenAI-compatible APIs behave identically. Some features (like streaming, certain response modes) may not work as expected.

---

## Future Considerations

### Potential Improvements

1. **Add Response Mode Fallback**
   ```python
   try:
       # Try using LlamaIndex synthesizer
       response = query_engine.query(question)
       if response.response == "Empty Response":
           raise ValueError("Synthesizer failed")
   except:
       # Fallback to custom implementation
       response = custom_query_engine.query(question)
   ```

2. **Add Model Validation on Startup**
   ```python
   def validate_model_name(api_base: str, model: str, api_key: str) -> bool:
       """Check if model exists before starting."""
       response = requests.get(f"{api_base}/models", headers={"Authorization": f"Bearer {api_key}"})
       available = [m["id"] for m in response.json()["data"]]
       return model in available
   ```

3. **Add Streaming Support Check**
   Some endpoints don't support streaming. Detect and disable automatically.

---

## References

- LlamaIndex Documentation: https://docs.llamaindex.ai/
- Response Synthesizers: https://docs.llamaindex.ai/en/stable/module_guides/querying/response_synthesizers/
- Custom OpenAI Endpoints: https://docs.llamaindex.ai/en/stable/examples/llm/openai_like/

---

## Related Issues

- Issue tracker: Consider reporting this to LlamaIndex maintainers
- Workaround: Use custom query engine for custom OpenAI endpoints
- Alternative: Try different response modes or implement manual synthesis

---

**Conclusion:** The issue was a combination of invalid model configuration and LlamaIndex's response synthesizer incompatibility with custom endpoints. The fix implements a direct RAG pipeline that bypasses the problematic abstraction layer.
