"""Log-style test outputs for Claude Code + headroom.

Each case prints a realistic, repetitive output with a hidden "answer" the
model must still find after compression. Ask Claude Code to run one and
answer the question; then check the dashboard for savings.

Run: python claude_code/logs.py <case>      (python claude_code/logs.py list  -> show cases)
"""

import random
import sys


def pytest_run():
    """Test run: 400 PASSED lines, 2 FAILED with assertion details."""
    rng = random.Random(1)
    out = ["============================= test session starts ==============================",
           "platform win32 -- Python 3.13.1, pytest-8.3.4", "collected 402 items", ""]
    for i in range(402):
        mod = rng.choice(["orders", "billing", "auth", "search", "users"])
        if i == 133:
            out.append(f"tests/test_billing.py::test_refund_rounding FAILED")
        elif i == 377:
            out.append(f"tests/test_auth.py::test_token_expiry FAILED")
        else:
            out.append(f"tests/test_{mod}.py::test_case_{i:03d} PASSED")
    out += ["", "=================================== FAILURES ===================================",
            "___________________________ test_refund_rounding ___________________________",
            "    def test_refund_rounding():",
            ">       assert refund(10.005) == 10.01",
            "E       AssertionError: assert 10.0 == 10.01",
            "tests/test_billing.py:88: AssertionError",
            "___________________________ test_token_expiry ___________________________",
            ">       assert token.expires_in == 3600",
            "E       AssertionError: assert 360 == 3600",
            "tests/test_auth.py:41: AssertionError",
            "=========================== 2 failed, 400 passed in 12.31s ==========================="]
    return "\n".join(out)


def build_output():
    """Build: 300 compile lines + deprecation warnings, 1 real error at the end."""
    out = []
    for i in range(300):
        out.append(f"[INFO] Compiling module-{i % 25}/src/main/java/com/example/Service{i}.java")
        if i % 40 == 0:
            out.append(f"[WARNING] Service{i}.java: uses deprecated API java.util.Date#getYear()")
    out += ["[ERROR] /src/main/java/com/example/PaymentGateway.java:[142,17] cannot find symbol",
            "[ERROR]   symbol:   method chargeCard(java.lang.String,int)",
            "[ERROR]   location: class com.example.StripeClient",
            "[INFO] BUILD FAILURE", "[INFO] Total time: 01:42 min"]
    return "\n".join(out)


def multi_errors():
    """App log: 1000 INFO lines with 3 *different* errors scattered in it."""
    rng = random.Random(3)
    errors = {
        150: "ERROR payment: card declined for order ORD-8812 (insufficient_funds)",
        610: "ERROR storage: disk usage 97% on /var/lib/postgresql",
        905: "ERROR auth: JWT signature verification failed for user u-4471",
    }
    out = []
    for i in range(1000):
        ts = f"2026-10-08T09:{i // 60 % 60:02d}:{i % 60:02d}Z"
        out.append(f"{ts} {errors[i]}" if i in errors else
                   f"{ts} INFO http: {rng.choice(['GET', 'POST'])} /api/v2/items/{rng.randint(1, 999)} 200 {rng.randint(5, 80)}ms")
    return "\n".join(out)


def stack_trace():
    """Log with a Java exception: 200 INFO lines, then a 30-line stack trace."""
    out = [f"2026-10-08 10:00:{i % 60:02d} INFO  [worker-{i % 8}] Processed batch {i}" for i in range(200)]
    out.append("2026-10-08 10:03:21 ERROR [worker-3] Batch 201 failed")
    out.append("java.lang.NullPointerException: Cannot invoke \"Customer.getAddress()\" because \"customer\" is null")
    out.append("    at com.example.shipping.LabelPrinter.print(LabelPrinter.java:57)")
    out.append("    at com.example.shipping.ShipmentService.ship(ShipmentService.java:112)")
    out += [f"    at com.example.framework.Pipeline.step{i}(Pipeline.java:{200 + i})" for i in range(25)]
    out.append("    at java.base/java.lang.Thread.run(Thread.java:1583)")
    out += [f"2026-10-08 10:03:{22 + i:02d} INFO  [worker-{i % 8}] Processed batch {202 + i}" for i in range(30)]
    return "\n".join(out)


def repeated_error_count():
    """Same WARN repeated 57 times among INFO lines. Tests whether counts survive."""
    rng = random.Random(5)
    out, n = [], 0
    for i in range(800):
        if rng.random() < 0.07 and n < 57:
            n += 1
            out.append(f"2026-10-08T11:{i // 60 % 60:02d}:{i % 60:02d}Z WARN cache: redis timeout after 2000ms (key=session:{rng.randint(1000, 9999)})")
        else:
            out.append(f"2026-10-08T11:{i // 60 % 60:02d}:{i % 60:02d}Z INFO api: request ok")
    while n < 57:
        n += 1
        out.append("2026-10-08T11:59:59Z WARN cache: redis timeout after 2000ms (key=session:0000)")
    return "\n".join(out)


def latency_trend():
    """No error lines at all; latency slowly climbs from ~20ms to ~900ms. Tests a subtle signal."""
    out = []
    for i in range(500):
        ms = 20 + int((i / 500) ** 3 * 880)
        out.append(f"2026-10-08T12:{i // 60 % 60:02d}:{i % 60:02d}Z INFO api: GET /api/search 200 {ms}ms")
    return "\n".join(out)


def all_ok():
    """700 healthy INFO lines, no problems. Tests that the model does not invent an error."""
    return "\n".join(f"2026-10-08T13:{i // 60 % 60:02d}:{i % 60:02d}Z INFO api: GET /health 200 2ms" for i in range(700))


def huge_log():
    """5000-line log with one FATAL near the end. Shows savings at scale."""
    out = [f"2026-10-08T14:{i // 60 % 60:02d}:{i % 60:02d}Z INFO worker: job {i} done in {i % 90 + 10}ms" for i in range(5000)]
    out[4321] = "2026-10-08T15:12:01Z FATAL worker: out of memory (heap 4096MB) while processing job 4321"
    return "\n".join(out)


CASES = {
    "pytest": (pytest_run, "어떤 테스트가 실패했고 원인은 뭐야?", "test_refund_rounding, test_token_expiry"),
    "build": (build_output, "빌드가 왜 실패했어?", "PaymentGateway.java:142, chargeCard symbol"),
    "multi": (multi_errors, "에러를 전부 찾아줘", "3개: payment card declined / disk 97% / JWT"),
    "trace": (stack_trace, "무슨 예외가 어디서 났어?", "NullPointerException, LabelPrinter.java:57"),
    "count": (repeated_error_count, "redis timeout 경고가 몇 번 났어?", "57번 (압축 후 정확히 세는지 확인)"),
    "trend": (latency_trend, "이상한 점 있어?", "에러 없음, 지연시간이 20ms→900ms로 증가"),
    "ok": (all_ok, "문제 있어?", "문제 없음 (지어내지 않는지 확인)"),
    "huge": (huge_log, "뭐가 문제야?", "job 4321 out of memory"),
}

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in [*CASES, "list"]:
        sys.exit(f"usage: python claude_code/logs.py [{'|'.join(CASES)}|list]")
    if sys.argv[1] == "list":
        for k, (_, q, a) in CASES.items():
            print(f"{k:7} Q: {q:30} A: {a}")
    else:
        print(CASES[sys.argv[1]][0]())
