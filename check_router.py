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
