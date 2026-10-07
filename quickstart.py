import logging
import os
import sys

from dotenv import load_dotenv
from headroom import compress
from openai import OpenAI

load_dotenv()  # reads .env in the current directory
logging.basicConfig(level=logging.WARNING)  # show headroom warnings (e.g. why nothing was compressed)

model = os.getenv("OPENAI_MODEL")
base_url = os.getenv("OPENAI_BASE_URL")
api_key = os.getenv("OPENAI_API_KEY")

missing = [k for k, v in {"OPENAI_MODEL": model, "OPENAI_BASE_URL": base_url,
                          "OPENAI_API_KEY": api_key}.items() if not v]
if missing:
    sys.exit(f"Set {', '.join(missing)} in .env (see .env.example)")

# A long, repetitive tool output (300 log lines) -- the kind of content headroom compresses.
# A short user message alone has nothing to compress, so it would show "Saved 0 tokens".
log = "\n".join(
    "2026-10-07T04:31:07Z FATAL db-pool: connection refused to 10.0.3.17:5432"
    if i == 66
    else f"2026-10-07T04:{i // 60:02d}:{i % 60:02d}Z INFO api: GET /v1/items/{i % 50} 200 {i % 37 + 3}ms"
    for i in range(300)
)
messages = [
    {"role": "user", "content": "Analyze these results"},
    {
        "role": "assistant",
        "content": None,
        "tool_calls": [{"id": "call_0", "type": "function",
                        "function": {"name": "read_logs", "arguments": "{}"}}],
    },
    {"role": "tool", "tool_call_id": "call_0", "content": log},
    {"role": "user", "content": "What went wrong?"},
]
result = compress(messages, model=model)

client = OpenAI(api_key=api_key, base_url=base_url)
response = client.chat.completions.create(model=model, messages=result.messages)
print(response.choices[0].message.content)
print(f"Transforms: {result.transforms_applied}")
print(f"Tokens: {result.tokens_before} -> {result.tokens_after}")
print(f"Saved {result.tokens_saved} tokens ({result.compression_ratio:.0%})")
