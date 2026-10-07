# Claude Code + headroom + 대시보드

`headroom wrap claude`는 headroom 프록시를 띄운 뒤, Claude Code가 그 프록시를 거쳐 Anthropic에 요청하도록 실행합니다.

```
[Claude Code] ──▶ [headroom 프록시 :8787] ──압축해서──▶ [Anthropic]
                         │
                         └──▶ http://127.0.0.1:8787/dashboard (절약량)
```

## 0. 사전 점검 (한 번만)
프록시는 토큰을 세려고 tiktoken 파일을 인터넷에서 받습니다. 회사 SSL에 막히면 **아무것도 압축되지 않으므로** 먼저 확인합니다.
```powershell
python claude_code/setup_check.py
```
`[FAIL]`이 나오면:
```powershell
pip install pip-system-certs
python claude_code/setup_check.py      # 다시 확인, [OK] 두 줄이 나와야 함
```

## 1. Claude Code를 headroom으로 실행 (터미널 1)
```powershell
$env:HEADROOM_DISABLE_KOMPRESS="1"       # AI 압축 모델 끄기 (SSL로 다운로드 안 될 때)
headroom wrap claude --code-memory none
```
- `--code-memory none`: 코드 탐색 도구(Serena) 설치를 건너뜀. 회사망에서 설치가 막힐 수 있어서 빼 둠.
- 평소처럼 Claude Code 화면이 뜹니다. 로그인도 평소 방식 그대로입니다.
- 끝낸 뒤 원래대로 쓰려면 `claude`로 실행하면 됩니다 (`headroom unwrap claude`는 wrap이 바꾼 설정을 되돌림).

## 2. 대시보드 열기 (터미널 2)
```powershell
headroom dashboard
```
브라우저에서 http://127.0.0.1:8787/dashboard 가 열립니다. Claude Code를 쓰는 동안 실시간으로 갱신됩니다.

## 3. 절약이 보이게 Claude Code에 시켜 보기
headroom은 Claude Code가 **파일을 읽은 결과**(Read, Grep, Glob, WebFetch, `cat` 등)는 일부러 압축하지 않습니다.
Claude가 그 내용을 정확히 고쳐야 할 수 있기 때문입니다. 대신 **명령을 실행한 출력**은 압축합니다.

Claude Code에 이렇게 입력해 보세요.
```
python claude_code/emit.py log 를 실행하고, 서비스가 왜 실패하는지 알려줘
python claude_code/emit.py json 을 실행하고, 실패한 주문을 찾아줘
python claude_code/emit.py yaml 을 실행하고, replicas가 0인 서비스를 찾아줘
```
`emit.py`는 `scenarios/`의 데이터를 화면에 출력만 하는 스크립트입니다 (`log, json, grep, diff, code, csv, html, yaml, text`).

## 4. 대시보드 읽는 법
`dashboard-example.png`는 이 저장소의 9개 상황을 프록시에 보낸 뒤의 화면입니다 (테스트 환경이라 토큰 수는 실제와 다름).

| 위치 | 뜻 |
|---|---|
| **TOKENS SAVED** | 압축으로 줄인 토큰 수와 비율 |
| **COST SAVED** | 그만큼 아낀 금액 (모델 가격 기준 추정) |
| **Token Usage** | Before Compression(원래) → Proxy Removed(줄인 양) → After Compression(실제로 보낸 양) |
| **What Headroom Removed** | 무엇을 줄였는지 (JSON 군더더기, 공백 등) |
| **Prefix Cache Impact** | 압축 때문에 Anthropic 캐시가 깨진 손해와 비교한 순이익 (NET) |
| **Recent Requests** | 요청별 입력 토큰과 절약 비율. 행을 누르면 자세히 |

맨 위 `Session / Lifetime / Historical` 탭으로 이번 실행분, 누적, 기간별을 바꿔 볼 수 있습니다.
