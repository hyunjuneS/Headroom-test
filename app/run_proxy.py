"""vendor/headroom 의 headroom 프록시를 켠다 (대시보드 포함).

    python app/run_proxy.py

.env 의 OPENAI_BASE_URL 을 업스트림(실제 LLM)으로 사용한다.
`headroom` 명령어가 없어도 동작하도록 python -m 으로 실행한다.
"""

import os
import subprocess
import sys
from urllib.parse import urlparse

from dotenv import load_dotenv

load_dotenv()

base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
port = urlparse(os.getenv("HEADROOM_PROXY_URL", "http://127.0.0.1:8787")).port or 8787

# headroom 은 업스트림 주소를 /v1 없이 받는다 (요청 경로 /v1/... 를 그대로 붙임).
upstream = base_url[: -len("/v1")] if base_url.endswith("/v1") else base_url

# token: 이전 턴까지 적극적으로 압축 (압축 효과 확인용)
# cache: 이전 턴을 고정해 프롬프트 캐시 적중률을 우선 (headroom 기본값)
mode = os.getenv("HEADROOM_MODE", "token")

cmd = [
    sys.executable, "-m", "headroom.cli", "proxy",
    "--port", str(port),
    "--openai-api-url", upstream,
    "--mode", mode,
]
print("실행:", " ".join(cmd))
print(f"대시보드: http://127.0.0.1:{port}/dashboard")
sys.exit(subprocess.call(cmd))
