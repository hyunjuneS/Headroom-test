"""Scenario 5: source file - a Python module the agent opened to read."""

from _common import main


def build():
    funcs = []
    for i in range(40):
        funcs.append(
            f"def compute_metric_{i}(values: list[float], weight: float = 1.0) -> float:\n"
            f"    \"\"\"Compute metric {i} as a weighted mean of the values.\n\n"
            f"    Args:\n        values: Input samples.\n        weight: Scale factor.\n\n"
            f"    Returns:\n        The weighted mean, or 0.0 for an empty list.\n    \"\"\"\n"
            f"    if not values:\n        return 0.0\n"
            f"    total = sum(v * weight for v in values)\n"
            f"    return total / len(values)\n"
        )
    funcs.insert(23, "def apply_discount(price: float, rate: float) -> float:\n"
                     "    \"\"\"Apply a discount rate to a price.\"\"\"\n"
                     "    return price * rate  # BUG: should be price * (1 - rate)\n")
    return dict(
        title="5. Source code (Python module, 41 functions)",
        content="import math\nimport statistics\n\n\n" + "\n\n".join(funcs),
        question="Summarize what this module contains.",
        must_keep="def apply_discount",
        tool_name="read_file",
    )


if __name__ == "__main__":
    main(build)
