"""Scenario 9: plain prose - meeting notes (no repetition, no structure).

Without the ML text model, headroom has little to remove from prose.
This scenario shows that limit.
"""

from _common import main


def build():
    paragraphs = [
        "The team met on Tuesday to review the third-quarter roadmap and the open incidents.",
        "Minji reported that the payment service latency improved after the cache rollout, "
        "although the p99 is still above the target during the evening peak.",
        "Jisoo raised a concern about the vendor contract: the renewal deadline is October 31 "
        "and legal has not yet reviewed the new data processing terms.",
        "The group agreed to postpone the mobile redesign to the next quarter so that two "
        "engineers can focus on the search migration, which is now the top priority.",
        "Hyun suggested running a load test before Black Friday, using last year's traffic "
        "multiplied by 1.5 as the baseline, and volunteered to own the test plan.",
        "Action items were assigned, and the next review is scheduled for two weeks from now.",
    ] * 4
    return dict(
        title="9. Plain text (meeting notes)",
        content="\n\n".join(paragraphs),
        question="What is the contract renewal deadline?",
        must_keep="October 31",
        tool_name="read_doc",
    )


if __name__ == "__main__":
    main(build)
