# Headroom-test

Headroom(https://github.com/headroomlabs-ai/headroom)을 소스째 가져와 커스터마이징(xProvence 주입)하는 작업 레포.

## 구조

- `vendor/headroom/` — Headroom upstream 소스 (git subtree, squash). 여기를 직접 수정한다.
- `app/run_proxy.py` — vendor headroom 프록시 + 대시보드 실행
- `app/llm_call.py` — 프록시를 거쳐 LLM 을 한 번 호출하는 예제
- `tests/` — 커스텀 수정에 대한 테스트

## 설치 (Python 3.11.9)

### A. 소스 빌드 (Rust/cargo 필요)

```bash
pip install -e "vendor/headroom[proxy]"
```

### B. Rust 빌드 없이 (회사망 SSL 로 cargo 가 막힐 때)

PyPI wheel 에 들어있는 빌드된 Rust 모듈(`_core`)만 가져다 쓰고, Python 코드는 vendor 를 보게 한다.
vendor 버전(현재 0.44.0)과 같은 버전을 설치해야 한다.

```bash
pip install "headroom-ai[proxy]==0.44.0"
python -c "import headroom._core as c, shutil; print(shutil.copy(c.__file__, 'vendor/headroom/headroom/'))"
pip uninstall -y headroom-ai
python -c "import sysconfig, os; p=os.path.join(sysconfig.get_paths()['purelib'], 'headroom-vendor.pth'); open(p,'w').write(os.path.abspath('vendor/headroom')); print(p)"
```

공통:

```bash
pip install openai python-dotenv pytest
python -c "import headroom, headroom._core as c; print(headroom.__file__); print(c.__file__)"  # 둘 다 vendor 경로여야 함
```

## 실행

```bash
cp .env.example .env   # OPENAI_BASE_URL / OPENAI_API_KEY / OPENAI_MODEL 채우기
python app/run_proxy.py    # 터미널 1: 프록시 + 대시보드
python app/llm_call.py     # 터미널 2: LLM 호출
```

대시보드: http://127.0.0.1:8787/dashboard

회사망에서 Hugging Face 가 막혀 `OSError: We couldn't connect to 'https://huggingface.co'` 가 뜨면 `.env` 에 `HEADROOM_DISABLE_KOMPRESS=1` 을 둔다 (Kompress 텍스트 ML 모델만 꺼지고 로그/JSON/코드 압축은 동작).

## 커스텀 수정 내역 (vendor/headroom)

| 파일 | 내용 |
|---|---|
| `headroom/tokenizers/tiktoken_counter.py` | tiktoken vocab 다운로드 실패(SSL/프록시 차단) 시 압축 전체가 실패하던 문제 → 토큰 추정치로 폴백 |
| `headroom/proxy/server.py` | 대시보드가 5초마다 `/stats` 를 폴링할 때마다 찍히던 INFO 로그를 DEBUG 로 낮춤 (헬스체크와 동일 처리) |

## upstream 업데이트

```bash
git subtree pull --prefix=vendor/headroom https://github.com/headroomlabs-ai/headroom.git main --squash
```
