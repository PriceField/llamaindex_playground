"""Test script to generate curl command for Trend Micro API."""
import os
from dotenv import load_dotenv

load_dotenv()

api_token = os.getenv("API_KEY", "your_jwt_token_here")
api_base = os.getenv("API_BASE", "https://api.rdsec.trendmicro.com/prod/aiendpoint/v1")
model = os.getenv("MODEL_NAME", "claude-sonnet-4-5-20250929")

# Ensure API_BASE ends with /v1
if not api_base.endswith('/v1'):
    if api_base.endswith('/'):
        api_base = api_base + 'v1'
    else:
        api_base = api_base + '/v1'

endpoint = f"{api_base}/chat/completions"

print("=" * 70)
print("CURL COMMAND FOR TESTING")
print("=" * 70)
print()
print("Test the /chat/completions endpoint:")
print()
print(f'curl -X POST "{endpoint}" \\')
print(f'  -H "Authorization: Bearer {api_token}" \\')
print('  -H "Content-Type: application/json" \\')
print('  -d \'{')
print(f'    "model": "{model}",')
print('    "messages": [')
print('      {"role": "user", "content": "Say hello in one sentence."}')
print('    ],')
print('    "max_tokens": 100')
print('  }\'')
print()
print("=" * 70)
print()
print("Or test the /messages endpoint (Anthropic native):")
print()
messages_endpoint = f"{api_base}/messages"
print(f'curl -X POST "{messages_endpoint}" \\')
print(f'  -H "Authorization: Bearer {api_token}" \\')
print('  -H "Content-Type: application/json" \\')
print('  -d \'{')
print(f'    "model": "{model}",')
print('    "messages": [')
print('      {"role": "user", "content": "Say hello in one sentence."}')
print('    ],')
print('    "max_tokens": 100')
print('  }\'')
print()
print("=" * 70)
print()
print(f"Current API_BASE: {api_base}")
print(f"Chat completions endpoint: {endpoint}")
print(f"Messages endpoint: {messages_endpoint}")
