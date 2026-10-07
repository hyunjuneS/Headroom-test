"""Scenario 2: JSON API response - 200 order records, one of them failed."""

import json
import random

from _common import main


def build():
    rng = random.Random(2)
    orders = []
    for i in range(200):
        orders.append({
            "order_id": f"ORD-{10000 + i}",
            "customer_id": f"CUST-{rng.randint(1, 40):03d}",
            "status": "PAYMENT_FAILED" if i == 137 else "DELIVERED",
            "amount": round(rng.uniform(5, 300), 2),
            "currency": "KRW",
            "items": rng.randint(1, 5),
            "warehouse": rng.choice(["ICN-1", "ICN-2", "PUS-1"]),
            "created_at": f"2026-10-0{rng.randint(1, 7)}T{rng.randint(0, 23):02d}:00:00Z",
        })
    return dict(
        title="2. JSON API response (200 orders, 1 failed)",
        content=json.dumps(orders, indent=2),
        question="Which order failed and why?",
        must_keep="ORD-10137",
        tool_name="list_orders",
    )


if __name__ == "__main__":
    main(build)
