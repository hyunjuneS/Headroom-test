"""A fake OpenAI server for trying the proxy without an API key or cost.

It answers /v1/chat/completions with a fixed reply and prints how big the
request it received was, so you can see what headroom actually forwarded.

Run: python proxy/fake_openai.py        (listens on http://127.0.0.1:9000)
"""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 9000


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
        messages = body.get("messages", [])
        chars = sum(len(m.get("content") or "") for m in messages if isinstance(m.get("content"), str))
        print(f"[fake-openai] {self.path}: {len(messages)} messages, {chars:,} chars of content received")
        reply = {
            "id": "chatcmpl-fake",
            "object": "chat.completion",
            "created": 0,
            "model": body.get("model", "fake"),
            "choices": [{"index": 0, "finish_reason": "stop",
                         "message": {"role": "assistant",
                                     "content": f"(fake reply) I received {chars:,} chars."}}],
            "usage": {"prompt_tokens": chars // 4, "completion_tokens": 8, "total_tokens": chars // 4 + 8},
        }
        data = json.dumps(reply).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    print(f"Fake OpenAI listening on http://127.0.0.1:{PORT}  (Ctrl+C to stop)")
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
