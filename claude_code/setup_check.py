"""Pre-flight check before running Claude Code through headroom.

The headroom proxy counts tokens with tiktoken, which downloads its vocab
files from openaipublic.blob.core.windows.net on first use. If that download
fails (e.g. SSL errors behind a corporate proxy), the proxy forwards every
request UNCOMPRESSED. This script downloads them once into the local cache.

Run: python claude_code/setup_check.py
"""

import os
import sys
import tempfile

import tiktoken

ok = True
for name in ("cl100k_base", "o200k_base"):  # cl100k: Claude models, o200k: GPT-4o and newer
    try:
        tiktoken.get_encoding(name)
        print(f"[OK]   tiktoken {name}")
    except Exception as e:  # noqa: BLE001
        ok = False
        print(f"[FAIL] tiktoken {name}: {type(e).__name__}: {str(e)[:200]}")

cache = os.environ.get("TIKTOKEN_CACHE_DIR") or os.path.join(tempfile.gettempdir(), "data-gym-cache")
print(f"\ntiktoken cache: {cache}")

if ok:
    print("\nAll set. Start Claude Code with: headroom wrap claude --code-memory none")
    sys.exit(0)

print(
    "\nThe download failed. On a corporate network this is usually SSL inspection.\n"
    "Fix: pip install pip-system-certs   (lets Python trust the Windows certificate store)\n"
    "then run this script again. Until it passes, the proxy will not compress anything."
)
sys.exit(1)
