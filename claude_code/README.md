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
$env:HEADROOM_DISABLE_KOMPRESS="1"            # AI 압축 모델 끄기 (SSL로 다운로드 안 될 때)
$env:HEADROOM_DISABLE_KOMPRESS_FALLBACK="1"   # 위 설정만으로는 남는 내용을 여전히 AI 모델로 보냄 → 이것도 꺼야 완전히 꺼짐
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

### 요청별로 보기: Recent Requests
맨 아래 **Recent Requests** 표에서 요청 하나하나를 봅니다 (`dashboard-recent-requests.png`). 최근 25개, 맨 위가 최신입니다.

| 열 | 뜻 |
|---|---|
| INPUT | **압축 후** 실제로 보낸 입력 토큰 |
| MSG SAVED | 그 요청에서 줄인 비율 |
| LATENCY | 걸린 시간 |

행을 누르면 펼쳐집니다: **ORIGINAL TOKENS**(원래) → **COMPRESSED TOKENS**(보낸 양), **TOKENS REMOVED**(줄인 양), **TRANSFORMS APPLIED**(사용한 압축기, 예: `router:log:0.03` = 로그 압축기로 3%까지 줄임).

Claude Code는 질문 하나에 요청을 여러 번 보냅니다 (도구 실행 전, 도구 결과를 받은 뒤, 제목 생성 등). `cat` 결과가 들어간 요청은 **명령 실행 직후의 요청**이고, 그 행의 MSG SAVED가 높게 나옵니다.

맨 위 `Session / Lifetime / Historical` 탭으로 이번 실행분, 누적, 기간별을 바꿔 볼 수 있습니다.

## 문제 해결

### `Claude Code has both ANTHROPIC_API_KEY ... and ANTHROPIC_AUTH_TOKEN ... set`
`~/.claude/settings.json`(Windows: `C:\Users\<이름>\.claude\settings.json`)의 `env`에 인증 키가 둘 다 있어서
headroom이 실행 전에 멈춘 것입니다. **둘 중 하나만** 남겨야 합니다.

| 남길 키 | 이런 경우 |
|---|---|
| `ANTHROPIC_AUTH_TOKEN` | 회사 게이트웨이를 씀 (`env`에 `ANTHROPIC_BASE_URL`이 회사 주소로 있음) |
| `ANTHROPIC_API_KEY` | Anthropic API 키(`sk-ant-...`)로 직접 결제 |

어느 쪽인지 모르면 사내 Claude Code 설치 안내나 담당자에게 확인하세요.

**방법 A — 이 프로젝트에서만 끄기 (권장, 전역 설정은 그대로)**
이 저장소 폴더에 `.claude/settings.local.json`을 만들고, 안 쓸 키를 빈 값으로 덮어씁니다.
```json
{
  "env": {
    "ANTHROPIC_API_KEY": ""
  }
}
```
(`ANTHROPIC_AUTH_TOKEN`을 끌 거면 그 이름으로 바꿉니다.) 이 파일은 `.gitignore`에 들어 있어 커밋되지 않습니다.

PowerShell로 만들 때는 BOM 없는 UTF-8로 써야 합니다 (`Out-File -Encoding utf8`은 Windows PowerShell 5.1에서 BOM을 붙여 headroom이 읽지 못함).
```powershell
[IO.File]::WriteAllText("$PWD\.claude\settings.local.json", '{ "env": { "ANTHROPIC_API_KEY": "" } }')
```
headroom이 각 설정 파일에서 무엇을 보는지(키 값은 빼고) 확인하려면, wrap을 실행하는 폴더에서:
```powershell
python <Headroom-test 경로>\claude_code\check_auth.py
```

**방법 B — 전역 설정에서 지우기**
`settings.json`을 백업한 뒤 `env`에서 안 쓰는 키 한 줄을 지웁니다. 모든 프로젝트의 Claude Code에 적용됩니다.

### `401 Invalid bearer token` / `Please run /login` (회사 게이트웨이 사용 시)
`headroom wrap`은 회사 게이트웨이 주소를 **터미널 환경변수 `ANTHROPIC_BASE_URL`에서만** 찾습니다.
주소가 `settings.json`에만 있으면 headroom이 그걸 모르고 Anthropic 본사(api.anthropic.com)로 보내서, 회사 토큰이 거부됩니다.

wrap 전에 같은 터미널에서 회사 주소를 넣어 주세요 (`settings.json`의 `ANTHROPIC_BASE_URL` 값 그대로).
```powershell
$env:ANTHROPIC_BASE_URL="https://회사-게이트웨이-주소"
headroom wrap claude --code-memory none
```
실행 시 `ANTHROPIC_BASE_URL=http://127.0.0.1:8787 → upstream https://회사-게이트웨이-주소` 줄이 나오면
`Claude Code → headroom → 회사 게이트웨이` 순서로 연결된 것입니다.
이전에 띄운 headroom 프록시가 남아 있으면 그걸 재사용해 예전 주소로 보낼 수 있으니, 안 되면 PC를 재시작하거나 남은 `headroom` 프로세스를 종료하고 다시 실행하세요.

## 로그 압축 테스트 (`logs/*.txt`)
저장소의 `logs/` 폴더에 정답이 하나씩 숨어 있는 로그 파일 8개가 있습니다.
Claude Code에 **`python logs/view.py <이름>`을 실행하라고** 시키세요.
```
python logs/view.py worker 를 실행하고, 그 출력만 보고 뭐가 문제인지 알려줘
```

> **`cat`으로 읽게 하면 압축되지 않습니다.** headroom 프록시는 `cat`/`head`/`tail`/`Read` 결과를 *파일 읽기*로 보고
> 그대로 둡니다 (Claude가 그 파일을 정확히 고쳐야 할 수 있어서). 실제 에이전트는 로그를 보통 `kubectl logs`, 빌드, 테스트 같은
> **프로그램 실행 결과**로 보므로, `view.py`가 그 역할을 합니다 (파일 내용을 그대로 출력).

프록시로 미리 돌려 본 결과 (Claude Code와 같은 요청 형식, 테스트용 토크나이저라 토큰 수는 실제와 다르고 비율만 참고):

| 파일 | 질문 | 정답 | 절약 |
|---|---|---|---|
| `worker` | 뭐가 문제야? | job 4321 out of memory | ~99% |
| `api` | 에러를 전부 찾아줘 | 3개: 카드 거절(ORD-8812) / 디스크 97% / JWT 검증 실패 | ~97% |
| `shipping` | 무슨 예외가 어디서 났어? | NullPointerException, LabelPrinter.java:57 | ~94% |
| `search` | 이상한 점 있어? | 에러 없음, 응답시간 20ms → 900ms 증가 | ~99% (**정답 줄이 전부 생략됨**) |
| `health` | 문제 있어? | 문제 없음 | ~99% |
| `cache` | redis timeout 경고가 몇 번 났어? | 57번 | ~1% |
| `build` | 빌드가 왜 실패했어? | PaymentGateway.java:142 | 0% (프록시가 효과 부족으로 원본 유지) |
| `pytest` | 어떤 테스트가 실패했어? | test_refund_rounding, test_token_expiry | 0% |

`search`는 INFO 줄 안에만 신호가 있어 headroom이 전부 생략합니다. Claude가 `headroom_retrieve`로 원본을 다시 가져와 맞히는지가 핵심입니다.

### 덤: `cat` vs `view.py` 비교
`cat logs/worker.txt 해서 뭐가 문제인지 알려줘`와 `python logs/view.py worker 를 실행하고 뭐가 문제인지 알려줘`를 각각 시켜 보고
대시보드 Recent Requests를 비교하면, `cat` 쪽은 절약이 거의 없습니다.

## 문제 해결

### `Claude Code has both ANTHROPIC_API_KEY ... and ANTHROPIC_AUTH_TOKEN ... set`
`~/.claude/settings.json`(Windows: `C:\Users\<이름>\.claude\settings.json`)의 `env`에 인증 키가 둘 다 있어서
headroom이 실행 전에 멈춘 것입니다. **둘 중 하나만** 남겨야 합니다.

| 남길 키 | 이런 경우 |
|---|---|
| `ANTHROPIC_AUTH_TOKEN` | 회사 게이트웨이를 씀 (`env`에 `ANTHROPIC_BASE_URL`이 회사 주소로 있음) |
| `ANTHROPIC_API_KEY` | Anthropic API 키(`sk-ant-...`)로 직접 결제 |

어느 쪽인지 모르면 사내 Claude Code 설치 안내나 담당자에게 확인하세요.

**방법 A — 이 프로젝트에서만 끄기 (권장, 전역 설정은 그대로)**
이 저장소 폴더에 `.claude/settings.local.json`을 만들고, 안 쓸 키를 빈 값으로 덮어씁니다.
```json
{
  "env": {
    "ANTHROPIC_API_KEY": ""
  }
}
```
(`ANTHROPIC_AUTH_TOKEN`을 끌 거면 그 이름으로 바꿉니다.) 이 파일은 `.gitignore`에 들어 있어 커밋되지 않습니다.

PowerShell로 만들 때는 BOM 없는 UTF-8로 써야 합니다 (`Out-File -Encoding utf8`은 Windows PowerShell 5.1에서 BOM을 붙여 headroom이 읽지 못함).
```powershell
[IO.File]::WriteAllText("$PWD\.claude\settings.local.json", '{ "env": { "ANTHROPIC_API_KEY": "" } }')
```
headroom이 각 설정 파일에서 무엇을 보는지(키 값은 빼고) 확인하려면, wrap을 실행하는 폴더에서:
```powershell
python <Headroom-test 경로>\claude_code\check_auth.py
```

**방법 B — 전역 설정에서 지우기**
`settings.json`을 백업한 뒤 `env`에서 안 쓰는 키 한 줄을 지웁니다. 모든 프로젝트의 Claude Code에 적용됩니다.

### `401 Invalid bearer token` / `Please run /login` (회사 게이트웨이 사용 시)
`headroom wrap`은 회사 게이트웨이 주소를 **터미널 환경변수 `ANTHROPIC_BASE_URL`에서만** 찾습니다.
주소가 `settings.json`에만 있으면 headroom이 그걸 모르고 Anthropic 본사(api.anthropic.com)로 보내서, 회사 토큰이 거부됩니다.

wrap 전에 같은 터미널에서 회사 주소를 넣어 주세요 (`settings.json`의 `ANTHROPIC_BASE_URL` 값 그대로).
```powershell
$env:ANTHROPIC_BASE_URL="https://회사-게이트웨이-주소"
headroom wrap claude --code-memory none
```
실행 시 `ANTHROPIC_BASE_URL=http://127.0.0.1:8787 → upstream https://회사-게이트웨이-주소` 줄이 나오면
`Claude Code → headroom → 회사 게이트웨이` 순서로 연결된 것입니다.
이전에 띄운 headroom 프록시가 남아 있으면 그걸 재사용해 예전 주소로 보낼 수 있으니, 안 되면 PC를 재시작하거나 남은 `headroom` 프로세스를 종료하고 다시 실행하세요.

## 로그 압축 테스트 (`logs/*.txt`)
저장소의 `logs/` 폴더에 정답이 하나씩 숨어 있는 로그 파일 8개가 있습니다.
Claude Code에 **`cat`으로 읽으라고** 시키세요 (예: `cat logs/worker.txt 해서 뭐가 문제인지 알려줘`).

> headroom은 Claude Code의 `Read` 도구 결과는 일부러 압축하지 않습니다 (Claude가 파일을 정확히 고쳐야 할 수 있어서).
> 그냥 "읽어줘"라고 하면 Claude가 `Read`를 쓰므로 절약이 0입니다. `cat`(명령 실행)으로 읽은 로그만 압축됩니다.

| 파일 | 질문 | 정답 | 압축 (`cat` 기준 예상) |
|---|---|---|---|
| `worker.txt` | 뭐가 문제야? | job 4321 out of memory | 79,727 → 189 |
| `api.txt` | 에러를 전부 찾아줘 | 3개: 카드 거절(ORD-8812) / 디스크 97% / JWT 검증 실패 | 18,147 → 464 |
| `shipping.txt` | 무슨 예외가 어디서 났어? | NullPointerException, LabelPrinter.java:57 | 4,304 → 264 |
| `build.txt` | 빌드가 왜 실패했어? | PaymentGateway.java:142, chargeCard 없음 | 6,116 → 842 |
| `cache.txt` | redis timeout 경고가 몇 번 났어? | 57번 | 거의 안 줄어듦 |
| `pytest.txt` | 어떤 테스트가 실패했어? | test_refund_rounding, test_token_expiry | 안 줄어듦 |
| `search.txt` | 이상한 점 있어? | 에러는 없고 응답시간이 20ms → 900ms로 증가 | 8,114 → 64 (**정답 줄이 전부 생략됨**) |
| `health.txt` | 문제 있어? | 문제 없음 | 거의 전부 생략 |

`search.txt`는 INFO 줄 안에만 신호가 있어 headroom이 전부 생략합니다. Claude가 `headroom_retrieve`로 원본을 다시 가져와 맞히는지가 핵심입니다.

### 덤: `Read` vs `cat` 비교
같은 파일을 `logs/worker.txt를 Read로 읽고 뭐가 문제인지 알려줘` / `cat logs/worker.txt 해서 뭐가 문제인지 알려줘`로 각각 시켜 보고 대시보드의 Recent Requests를 비교하면 차이가 보입니다.
`worker.txt`는 5,000줄이라 `Read`는 앞부분만 읽을 수 있어서, 4,322번째 줄의 정답을 못 볼 수도 있습니다.
