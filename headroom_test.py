"""Headroom compression test (no pytest).

Checks what the headroom README claims:
  1. compress() reduces tokens on repetitive tool output (logs, JSON).
  2. The important line (FATAL) survives compression byte for byte.
  3. optimize=False passes messages through unchanged.

Setup:
    pip install headroom-ai
Run:
    python headroom_test.py
"""

import json
import os
import random
import sys

os.environ.setdefault("HEADROOM_BEACON", "off")  # disable anonymous telemetry

from headroom import compress  # noqa: E402

MODEL = "gpt-4o"
FATAL_LINE = "2026-10-07T04:31:07Z FATAL db-pool: connection refused to 10.0.3.17:5432 (attempt 67)"


def make_log(n=300):
    random.seed(7)
    lines = []
    for i in range(n):
        if i == 66:
            lines.append(FATAL_LINE)
        else:
            lines.append(
                f"2026-10-07T04:{i // 60:02d}:{i % 60:02d}Z INFO api: "
                f"GET /v1/items/{random.randint(1, 50)} 200 {random.randint(3, 40)}ms"
            )
    return "\n".join(lines)


def make_search_results(n=100):
    random.seed(11)
    return json.dumps(
        [
            {
                "path": f"src/module_{i % 10}/file_{i}.py",
                "line": random.randint(1, 500),
                "score": round(random.random(), 3),
                "snippet": "def handle_request(self, request):",
            }
            for i in range(n)
        ]
    )


def run(tool_output):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Analyse the tool output and find the error."},
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {"id": "call_0", "type": "function",
                 "function": {"name": "read_logs", "arguments": "{}"}}
            ],
        },
        {"role": "tool", "tool_call_id": "call_0", "content": tool_output},
        {"role": "user", "content": "What went wrong?"},
    ]
    return messages, compress(messages, model=MODEL)


failures = 0


def check(name, ok, detail=""):
    global failures
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")
    if not ok:
        failures += 1


# 1 + 2. Log dump: tokens drop and the FATAL line survives
_, r = run(make_log())
check("log: tokens reduced", r.tokens_saved > 0,
      f"({r.tokens_before} -> {r.tokens_after}, {r.compression_ratio:.0%} saved)")
all_text = json.dumps(r.messages, ensure_ascii=False)
check("log: FATAL line preserved", FATAL_LINE in all_text)

# 1. JSON search results: tokens drop
_, r = run(make_search_results())
check("json: tokens reduced", r.tokens_saved > 0,
      f"({r.tokens_before} -> {r.tokens_after}, {r.compression_ratio:.0%} saved)")

# 3. optimize=False is a passthrough
msgs, _ = run("short output")
r = compress(msgs, model=MODEL, optimize=False)
check("passthrough: messages unchanged", r.messages == msgs)

print(f"\n{'ALL PASSED' if failures == 0 else f'{failures} FAILED'}")
sys.exit(1 if failures else 0)
