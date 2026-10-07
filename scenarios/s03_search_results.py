"""Scenario 3: code search (grep) output - 150 matches across a repo."""

import random

from _common import main


def build():
    rng = random.Random(3)
    lines = []
    for i in range(150):
        mod = rng.choice(["api", "billing", "auth", "orders", "utils"])
        path = f"src/{mod}/{rng.choice(['handlers', 'services', 'models'])}/file_{i % 30}.py"
        if i == 91:
            lines.append(f"src/billing/services/refund.py:{212}:    def get_user_by_email(email):  # deprecated")
        else:
            lines.append(f"{path}:{rng.randint(1, 400)}:        user = get_user_by_id(user_id)")
    return dict(
        title="3. Code search results (150 grep matches)",
        content="\n".join(lines),
        question="Where is get_user_by_email defined?",
        must_keep="refund.py:212",
        tool_name="grep",
    )


if __name__ == "__main__":
    main(build)
