"""Print one scenario's tool output to stdout, for Claude Code to run.

Claude Code passes file reads (Read tool, cat, head, ...) through verbatim so it
can edit exact bytes, so asking it to *read* a big file shows no savings.
Asking it to *run a command* that prints the data is what headroom compresses.

Run: python claude_code/emit.py log        (also: json, grep, diff, csv, html, yaml, text)
"""

import importlib
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scenarios"))

SCENARIOS = {
    "log": "s01_server_log",
    "json": "s02_json_api",
    "grep": "s03_search_results",
    "diff": "s04_git_diff",
    "code": "s05_source_code",
    "csv": "s06_table_csv",
    "html": "s07_html_page",
    "yaml": "s08_config_yaml",
    "text": "s09_plain_text",
}

if len(sys.argv) != 2 or sys.argv[1] not in SCENARIOS:
    sys.exit(f"usage: python claude_code/emit.py [{'|'.join(SCENARIOS)}]")

print(importlib.import_module(SCENARIOS[sys.argv[1]]).build()["content"])
