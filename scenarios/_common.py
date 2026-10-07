"""Shared helper for the scenario scripts.

Each scenario builds one realistic tool output, sends it through headroom's
compress() the way an agent would (user question -> tool call -> tool output),
and prints how much it shrank and whether the key fact survived.

The ML text model is disabled (kompress_model="disabled"), so only the
rule-based compressors (log, JSON, search, diff, code, table, ...) run.
No API key or network is needed.
"""

import logging
import os
import sys
import time

os.environ.setdefault("HEADROOM_BEACON", "off")  # no anonymous telemetry
logging.basicConfig(level=logging.ERROR)  # hide tokenizer/ONNX fallback warnings

from headroom import compress  # noqa: E402

MODEL = "gpt-4o"
PREVIEW_LINES = 12


def run(title, content, question, must_keep, tool_name="run_tool", quiet=False):
    """Compress one tool output and report the result.

    must_keep: a string that must still be in the compressed output
               (the fact the model needs to answer the question).
    Returns a dict with the numbers, for run_all.py.
    """
    messages = [
        {"role": "user", "content": question},
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [{"id": "call_0", "type": "function",
                            "function": {"name": tool_name, "arguments": "{}"}}],
        },
        {"role": "tool", "tool_call_id": "call_0", "content": content},
    ]

    t0 = time.perf_counter()
    result = compress(messages, model=MODEL, kompress_model="disabled", diagnostics=True)
    ms = (time.perf_counter() - t0) * 1000

    tool = next(d for d in result.diagnostics or [] if d.role == "tool")
    compressed = next(m for m in result.messages if m.get("role") == "tool")["content"]
    saved_pct = (1 - tool.tokens_after / tool.tokens_before) * 100 if tool.tokens_before else 0.0
    kept = must_keep in compressed

    row = {
        "title": title,
        "before": tool.tokens_before,
        "after": tool.tokens_after,
        "saved_pct": saved_pct,
        "action": tool.action,
        "kept": kept,
        "ms": ms,
    }
    if quiet:
        return row

    print(f"=== {title} ===")
    print(f"Question       : {question}")
    print(f"Tool output    : {len(content.splitlines())} lines, {len(content):,} chars")
    print(f"Decision       : {tool.action}")
    print(f"Tokens         : {tool.tokens_before:,} -> {tool.tokens_after:,}  ({saved_pct:.0f}% saved, {ms:.0f} ms)")
    print(f"Key fact kept  : {'YES' if kept else 'NO'}  ({must_keep!r})")
    print(f"--- compressed output (first {PREVIEW_LINES} lines) ---")
    lines = compressed.splitlines()
    for line in lines[:PREVIEW_LINES]:
        print(f"  {line[:150]}")
    if len(lines) > PREVIEW_LINES:
        print(f"  ... ({len(lines) - PREVIEW_LINES} more lines)")
    print()
    return row


def main(build):
    """Entry point for a scenario file: build() returns run()'s keyword args."""
    row = run(**build())
    sys.exit(0 if row["kept"] else 1)
