"""Scenario 7: HTML page - a fetched web page full of markup and navigation."""

from _common import main


def build():
    nav = "".join(f'<li class="nav-item"><a class="nav-link" href="/docs/page{i}">Page {i}</a></li>\n'
                  for i in range(60))
    body = "".join(
        f'<div class="card"><h3 class="card-title">Release {i}</h3>'
        f'<p class="card-text">Minor fixes and performance improvements.</p></div>\n'
        for i in range(40)
    )
    html = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Changelog</title>"
        "<script src='/static/app.js'></script><link rel='stylesheet' href='/static/app.css'></head>\n"
        f"<body><nav><ul class='nav'>\n{nav}</ul></nav>\n<main>\n"
        "<div class='card'><h3 class='card-title'>Release 4.0</h3>"
        "<p class='card-text'>BREAKING: the /v1/users endpoint was removed.</p></div>\n"
        f"{body}</main><footer>(c) 2026 Example Corp</footer></body></html>"
    )
    return dict(
        title="7. HTML web page (changelog)",
        content=html,
        question="Are there any breaking changes?",
        must_keep="/v1/users endpoint was removed",
        tool_name="fetch_url",
    )


if __name__ == "__main__":
    main(build)
