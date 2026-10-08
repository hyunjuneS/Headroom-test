"""Show which Claude settings files `headroom wrap claude` reads, and which auth
keys each one sets. Key VALUES are never printed, only set / empty / absent.

Run it from the folder where you run `headroom wrap claude`:
    python <path-to>/Headroom-test/claude_code/check_auth.py
"""

import json
import os
from pathlib import Path

import headroom
from headroom.cli import wrap
from headroom.providers.claude.vscode import claude_user_settings_path

KEYS = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN", "ANTHROPIC_BASE_URL")

print(f"headroom version   : {headroom.__version__}")
print(f"current folder     : {Path.cwd()}")
print(f"CLAUDE_CONFIG_DIR  : {os.environ.get('CLAUDE_CONFIG_DIR') or '(not set)'}")
print()

layers = [
    ("1 user", claude_user_settings_path()),
    ("2 project", Path.cwd() / ".claude" / "settings.json"),
    ("3 project local", Path.cwd() / ".claude" / "settings.local.json"),
]
for label, path in layers:
    print(f"[{label}] {path}")
    if not path.exists():
        print("    (file does not exist)")
        continue
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        print("    !! file starts with a UTF-8 BOM - headroom cannot read it. Re-save as 'UTF-8' (no BOM).")
        raw = raw[3:]
    try:
        env = json.loads(raw.decode("utf-8")).get("env") or {}
    except Exception as e:  # noqa: BLE001
        print(f"    !! not valid JSON: {e}")
        continue
    for k in KEYS:
        state = "absent" if k not in env else ("EMPTY (clears it)" if not str(env[k]).strip() else "set")
        if k == "ANTHROPIC_BASE_URL" and state == "set":
            state = f"set -> {env[k]}"
        print(f"    {k:22} {state}")

print("[4 shell environment]")
for k in KEYS[:2]:
    print(f"    {k:22} {'set' if os.environ.get(k, '').strip() else 'absent'}")
print()

try:
    wrap._raise_on_claude_auth_conflict(
        user_settings_path=layers[0][1],
        project_settings_path=layers[1][1],
        project_local_settings_path=layers[2][1],
        environ=dict(os.environ),
    )
    print("RESULT: no auth conflict - `headroom wrap claude` should get past this check.")
except Exception as e:  # noqa: BLE001
    print(f"RESULT: {e}")
