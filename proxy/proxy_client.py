"""Send the scenario data to OpenAI *through* the headroom proxy.

The app code is a normal OpenAI client; the only change is base_url, which
points at the proxy (http://127.0.0.1:8787/v1). The proxy compresses the
request and forwards it to the real API (or to fake_openai.py for testing).

Run (with the proxy already started, see proxy/README.md):
    python proxy/proxy_client.py            # all scenarios
    python proxy/proxy_client.py 1 2        # only scenarios 1 and 2
"""

import importlib
import json
import os
import pathlib
import sys
import urllib.request

from dotenv import load_dotenv
from openai import OpenAI

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scenarios"))
load_dotenv(ROOT / ".env")

PROXY_URL = os.getenv("HEADROOM_PROXY_URL", "http://127.0.0.1:8787")
model = os.getenv("OPENAI_MODEL", "gpt-4o")
# The proxy forwards your key to the upstream API. With fake_openai.py any value works.
client = OpenAI(base_url=f"{PROXY_URL}/v1", api_key=os.getenv("OPENAI_API_KEY") or "dummy")


def proxy_stats():
    with urllib.request.urlopen(f"{PROXY_URL}/stats", timeout=10) as r:
        return json.load(r)


def tokens_saved_so_far():
    return proxy_stats().get("tokens", {}).get("saved", 0)


wanted = set(sys.argv[1:])
paths = sorted((ROOT / "scenarios").glob("s[0-9][0-9]_*.py"))
for path in paths:
    if wanted and path.stem[1:3].lstrip("0") not in wanted:
        continue
    s = importlib.import_module(path.stem).build()
    messages = [
        {"role": "user", "content": s["question"]},
        {"role": "assistant", "content": None, "tool_calls": [
            {"id": "call_0", "type": "function", "function": {"name": s["tool_name"], "arguments": "{}"}}]},
        {"role": "tool", "tool_call_id": "call_0", "content": s["content"]},
    ]
    before = tokens_saved_so_far()
    resp = client.chat.completions.create(model=model, messages=messages)
    saved = tokens_saved_so_far() - before
    print(f"=== {s['title']} ===")
    print(f"Sent           : {len(s['content']):,} chars of tool output")
    print(f"Proxy saved    : {saved:,} tokens")
    print(f"Upstream usage : {resp.usage.prompt_tokens:,} prompt tokens (what you are billed for)")
    print(f"Answer         : {resp.choices[0].message.content[:200]}")
    print()

print("Proxy totals (GET /stats -> tokens):")
print(json.dumps(proxy_stats().get("tokens", {}), indent=2, ensure_ascii=False))
