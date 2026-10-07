"""Run every scenario and print one summary table.

Run: python scenarios/run_all.py          (summary only)
     python scenarios/run_all.py -v       (also print each scenario's details)
"""

import importlib
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))

from _common import run  # noqa: E402

verbose = "-v" in sys.argv[1:]
rows = []
for path in sorted(pathlib.Path(__file__).parent.glob("s[0-9][0-9]_*.py")):
    module = importlib.import_module(path.stem)
    rows.append(run(**module.build(), quiet=not verbose))

print(f"{'Scenario':46} {'Before':>7} {'After':>7} {'Saved':>6}  {'Kept':4}  Decision")
print("-" * 100)
for r in rows:
    print(f"{r['title']:46} {r['before']:>7,} {r['after']:>7,} {r['saved_pct']:>5.0f}%  "
          f"{'YES' if r['kept'] else 'NO':4}  {r['action']}")
total_before = sum(r["before"] for r in rows)
total_after = sum(r["after"] for r in rows)
print("-" * 100)
print(f"{'TOTAL':46} {total_before:>7,} {total_after:>7,} {(1 - total_after / total_before) * 100:>5.0f}%")
