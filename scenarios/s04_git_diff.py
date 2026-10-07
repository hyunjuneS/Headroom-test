"""Scenario 4: git diff - a large refactor touching many files."""

from _common import main


def build():
    parts = []
    for f in range(25):
        parts.append(
            f"diff --git a/src/handlers/h{f}.py b/src/handlers/h{f}.py\n"
            f"index 1a2b3c{f:02d}..4d5e6f{f:02d} 100644\n"
            f"--- a/src/handlers/h{f}.py\n"
            f"+++ b/src/handlers/h{f}.py\n"
            f"@@ -10,12 +10,12 @@ class Handler{f}:\n"
            "     def handle(self, request):\n"
            "         \"\"\"Handle the incoming request.\"\"\"\n"
            "-        logger = logging.getLogger(__name__)\n"
            "+        logger = get_logger(__name__)\n"
            "         payload = request.json()\n"
            "         validate(payload)\n"
            + ("-        timeout = 30\n+        timeout = 3  # TODO: was 30, typo?\n" if f == 17 else "")
            + "         result = self.service.process(payload)\n"
            "         return Response(result)\n"
        )
    return dict(
        title="4. git diff (25 files refactored)",
        content="".join(parts),
        question="Did this refactor change any behaviour besides the logger?",
        must_keep="timeout = 3",
        tool_name="git_diff",
    )


if __name__ == "__main__":
    main(build)
