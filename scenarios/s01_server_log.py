"""Scenario 1: server log - 300 repetitive INFO lines with one FATAL error."""

from _common import main

FATAL = "2026-10-07T04:31:07Z FATAL db-pool: connection refused to 10.0.3.17:5432"


def build():
    lines = [
        FATAL if i == 66 else
        f"2026-10-07T04:{i // 60:02d}:{i % 60:02d}Z INFO api: GET /v1/items/{i % 50} 200 {i % 37 + 3}ms"
        for i in range(300)
    ]
    return dict(
        title="1. Server log (300 lines, 1 FATAL)",
        content="\n".join(lines),
        question="Why is the service failing?",
        must_keep="FATAL db-pool: connection refused",
        tool_name="read_logs",
    )


if __name__ == "__main__":
    main(build)
