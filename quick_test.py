"""Quick test - directly test the query."""
import os
import sys
from dotenv import load_dotenv

# Fix Windows console encoding for Chinese characters
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

from src.app_factory import AppFactory

print("\n" + "="*70)
print("QUICK AI QUERY TEST")
print("="*70)

# Create and load
orchestrator = AppFactory.create_indexing_orchestrator(
    index_name="gpt-model-handler",
    require_llm=True
)
orchestrator.load_existing_index()

# Query with the traditional Chinese question you mentioned
print("\n用繁體中文介紹這個代碼庫：")
orchestrator.query("introduce repo by traditional chinese", top_k=5)

print("\n" + "="*70)
print("完成!")
print("="*70)
