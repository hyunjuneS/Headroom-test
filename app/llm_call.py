"""headroom 프록시를 거쳐 LLM을 한 번 호출하는 예제.

먼저 다른 터미널에서 프록시를 켠다 (README 참고). 그 다음:
    python app/llm_call.py

요청 흐름: 이 스크립트 -> headroom 프록시(압축) -> OPENAI_BASE_URL(실제 LLM)
대시보드: http://127.0.0.1:8787/dashboard
"""

import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

model = os.getenv("OPENAI_MODEL", "gpt-4o")
api_key = os.getenv("OPENAI_API_KEY")
proxy_url = os.getenv("HEADROOM_PROXY_URL", "http://127.0.0.1:8787").rstrip("/")
if not api_key:
    sys.exit("OPENAI_API_KEY 를 .env 에 넣어주세요 (.env.example 참고)")

# 압축 효과를 보려면 긴 툴 출력이 있어야 한다. 짧은 질문만 보내면 줄일 게 없다.
log = "\n".join(
    "2026-10-07T04:31:07Z FATAL db-pool: connection refused to 10.0.3.17:5432"
    if i == 66
    else f"2026-10-07T04:{i // 60:02d}:{i % 60:02d}Z INFO api: GET /v1/items/{i % 50} 200 {i % 37 + 3}ms"
    for i in range(300)
)
messages = [
    {"role": "user", "content": "서버 로그를 확인해줘"},
    {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {"id": "call_0", "type": "function", "function": {"name": "read_logs", "arguments": "{}"}}
        ],
    },
    {"role": "tool", "tool_call_id": "call_0", "content": log},
    {"role": "user", "content": "무엇이 잘못됐는지 한 문장으로 알려줘."},
]

# base_url 을 프록시로 지정하는 것만으로 headroom 이 끼어든다.
client = OpenAI(api_key=api_key, base_url=f"{proxy_url}/v1")
response = client.chat.completions.create(model=model, messages=messages)

print("답변:", response.choices[0].message.content)
print("usage:", response.usage)
print(f"대시보드: {proxy_url}/dashboard")
