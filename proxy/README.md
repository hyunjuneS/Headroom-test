# headroom 프록시 방식 테스트

프록시 방식은 앱 코드를 고치지 않고 **OpenAI 주소(base_url)만 프록시로 바꾸는** 방식입니다.

```
[앱] ──요청──▶ [headroom 프록시 :8787] ──압축된 요청──▶ [OpenAI 또는 fake_openai :9000]
```

## 파일
| 파일 | 역할 |
|---|---|
| `fake_openai.py` | 가짜 OpenAI 서버. 키·비용 없이 테스트할 때 사용. 실제로 전달받은 글자 수를 출력 |
| `proxy_client.py` | `scenarios/`의 9개 상황을 프록시를 거쳐 보내고, 절약량과 답변을 출력 |

## A. 가짜 OpenAI로 테스트 (API 키 없이)
터미널 3개를 엽니다.

**터미널 1 — 가짜 OpenAI 서버**
```bash
python proxy/fake_openai.py
```

**터미널 2 — headroom 프록시** (요청을 가짜 서버로 전달)
```bash
headroom proxy --port 8787 --openai-api-url http://127.0.0.1:9000 --disable-kompress --no-cache
```
"Uvicorn running on http://127.0.0.1:8787"가 나오면 준비 완료입니다.

**터미널 3 — 클라이언트**
```bash
python proxy/proxy_client.py        # 9개 상황 전부
python proxy/proxy_client.py 1 2    # 1, 2번만
```
터미널 1에 `chars of content received`로 OpenAI가 실제로 받은 글자 수가 찍힙니다.

## B. 진짜 OpenAI로 테스트
1. `.env`에 `OPENAI_API_KEY`, `OPENAI_MODEL`을 넣습니다.
2. 프록시를 실제 API 주소로 띄웁니다. 주소에는 `/v1`을 **붙이지 않습니다** (프록시가 붙임).
   ```bash
   headroom proxy --port 8787 --openai-api-url https://api.openai.com --disable-kompress --no-cache
   ```
3. `python proxy/proxy_client.py`

## 옵션 설명
| 옵션 | 뜻 |
|---|---|
| `--openai-api-url` | 압축한 요청을 보낼 실제 주소 (기본값: OpenAI) |
| `--disable-kompress` | AI 압축 모델을 쓰지 않음 (회사 SSL 문제로 다운로드가 안 될 때) |
| `--no-cache` | 같은 질문을 다시 보내면 프록시가 저장해 둔 답을 돌려주는 기능을 끔. 테스트를 반복할 때 필요 |

## 압축이 0일 때 확인할 것
프록시 터미널(터미널 2)에 아래 경고가 보이면 압축이 실패하고 원본이 그대로 전달된 것입니다.
```
Optimization failed: ... openaipublic.blob.core.windows.net ... (request forwarded unoptimized)
```
프록시는 토큰 수를 세려고 OpenAI 토크나이저 파일을 `openaipublic.blob.core.windows.net`에서 내려받습니다.
회사 네트워크에서 SSL 에러로 막히면 압축 전체가 건너뛰어집니다 (라이브러리 방식은 추정치로 대신하지만 프록시는 그렇지 않음).
`pip install pip-system-certs`로 파이썬이 Windows 인증서를 쓰게 한 뒤 프록시를 다시 띄워 보세요.
