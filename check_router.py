"""Show which compressor headroom picks for the quickstart log, and why.

Run: python check_router.py
"""
import logging
import platform

import headroom
from headroom.transforms.content_router import ContentRouter, _detect_content

logging.basicConfig(level=logging.WARNING)

log = "\n".join(
    "2026-10-07T04:31:07Z FATAL db-pool: connection refused to 10.0.3.17:5432"
    if i == 66
    else f"2026-10-07T04:{i // 60:02d}:{i % 60:02d}Z INFO api: GET /v1/items/{i % 50} 200 {i % 37 + 3}ms"
    for i in range(300)
)

print(f"headroom {headroom.__version__} / Python {platform.python_version()} / {platform.system()} {platform.release()}")
det = _detect_content(log)
print(f"Detected type : {det.content_type} (confidence {det.confidence:.2f})")
r = ContentRouter().compress(log)
print(f"Strategy used : {r.strategy_used}")
print(f"Ratio         : {r.compression_ratio:.2f}  (len {len(log)} -> {len(r.compressed)} chars)")
print(f"Routing log   : {r.routing_log}")

# --- Same log inside the full compress() pipeline, timed ---
# compress() gives the router a 20s deadline (HEADROOM_COMPRESSION_DEADLINE_MS);
# if model loading/downloads make it slower, the log passes through uncompressed.
import time

from headroom import compress

messages = [
    {"role": "user", "content": "Analyze these results"},
    {"role": "assistant", "content": None, "tool_calls": [
        {"id": "call_0", "type": "function", "function": {"name": "read_logs", "arguments": "{}"}}]},
    {"role": "tool", "tool_call_id": "call_0", "content": log},
    {"role": "user", "content": "What went wrong?"},
]
for label, kwargs in [("compress()", {}), ("compress(kompress_model='disabled')", {"kompress_model": "disabled"})]:
    t0 = time.perf_counter()
    res = compress(messages, model="gpt-4o", diagnostics=True, **kwargs)
    secs = time.perf_counter() - t0
    tool = next(d for d in res.diagnostics or [] if d.role == "tool")
    print(f"{label:38} {secs:6.1f}s  tool: {tool.tokens_before} -> {tool.tokens_after}  {tool.action}")
