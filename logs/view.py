"""Print one log file, like `kubectl logs` / `docker logs` would.

headroom treats `cat`/`head`/`tail` output as a *file read* and leaves it
uncompressed (the agent may need exact bytes to edit the file). Real agents
usually see logs as the output of a program, which headroom does compress.

Run: python logs/view.py <name>     (worker, api, shipping, build, cache, pytest, search, health)
"""

import pathlib
import sys

here = pathlib.Path(__file__).resolve().parent
names = sorted(p.stem for p in here.glob("*.txt"))
if len(sys.argv) != 2 or sys.argv[1] not in names:
    sys.exit(f"usage: python logs/view.py [{'|'.join(names)}]")
sys.stdout.write((here / f"{sys.argv[1]}.txt").read_text(encoding="utf-8"))
