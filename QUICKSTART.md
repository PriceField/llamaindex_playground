# Quick Start Guide

## 1. Activate Virtual Environment

**Windows (PowerShell/CMD):**
```bash
.venv\Scripts\activate
```

**Windows (Git Bash):**
```bash
source .venv/Scripts/activate
```

## 2. Set Up Your API Key

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:
```
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

Get your key here: https://console.anthropic.com/settings/keys

## 3. Run the Example

```bash
python src/main.py
```

## 4. Next Steps

### Try Document Querying (RAG)

1. Create a `data/` folder:
   ```bash
   mkdir data
   ```

2. Add some text files to `data/`

3. Edit `src/main.py` and uncomment the document query code

4. Run again: `python src/main.py`

### Learn More

- **LlamaIndex docs**: https://docs.llamaindex.ai/
- **Claude models**: https://docs.anthropic.com/claude/docs/models-overview
- **Example code**: Check out `src/main.py` for working examples

## Common Commands

```bash
make help          # Show all available commands
make run           # Run the application
make test          # Run tests
make fmt           # Format code with black
make lint          # Check code quality
```

## Troubleshooting

**Virtual environment not activated?**
- You should see `(.venv)` at the start of your command prompt
- Rerun the activation command from step 1

**Import errors?**
- Make sure you activated the virtual environment
- Try: `pip install -r requirements.txt`

**API key errors?**
- Check that `.env` file exists and has your key
- Verify the key starts with `sk-ant-`
