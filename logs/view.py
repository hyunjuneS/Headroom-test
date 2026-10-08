"""Print one log file, like `kubectl logs` / `docker logs` would.

headroom treats `cat`/`head`/`tail` output as a *file read* and leaves it
uncompressed (the agent may need exact bytes to edit the file). Real agents
usually see logs as the output of a program, which headroom does compress.

Run: python logs/view.py <name>     (worker, api, ..., orders, users, metrics)
"""

import pathlib
import sys

here = pathlib.Path(__file__).resolve().parent
files = {p.stem: p for p in sorted(here.glob("*.txt")) + sorted(here.glob("*.json"))}
names = list(files)
if len(sys.argv) != 2 or sys.argv[1] not in names:
    sys.exit(f"usage: python logs/view.py [{'|'.join(names)}]")
sys.stdout.write(files[sys.argv[1]].read_text(encoding="utf-8"))
