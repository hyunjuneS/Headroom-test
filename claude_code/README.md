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
