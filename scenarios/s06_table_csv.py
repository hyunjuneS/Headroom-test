"""Scenario 6: CSV table - a database query result with 300 rows."""

import random

from _common import main


def build():
    rng = random.Random(6)
    rows = ["employee_id,name,department,office,salary,status"]
    for i in range(300):
        status = "ON_LEAVE" if i == 211 else "ACTIVE"
        rows.append(f"E{1000 + i},Employee {i},{rng.choice(['Sales', 'R&D', 'HR', 'Ops'])},"
                    f"{rng.choice(['Seoul', 'Busan', 'Daejeon'])},{rng.randint(40, 120) * 1000},{status}")
    return dict(
        title="6. CSV table (DB query, 300 rows)",
        content="\n".join(rows),
        question="Which employee is on leave?",
        must_keep="E1211",
        tool_name="sql_query",
    )


if __name__ == "__main__":
    main(build)
