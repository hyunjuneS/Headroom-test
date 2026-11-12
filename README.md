# Headroom-test

Headroom(https://github.com/headroomlabs-ai/headroom)을 소스째 가져와 커스터마이징(xProvence 주입)하는 작업 레포.

## 구조

- `vendor/headroom/` — Headroom upstream 소스 (git subtree, squash). 여기를 직접 수정한다.

## 설치 (editable)

```bash
uv venv .venv --python 3.13
uv pip install --python .venv/bin/python -e vendor/headroom
```

- Python 코드(`vendor/headroom/headroom/**.py`) 수정은 재설치 없이 바로 반영된다.
- Rust 코드(`vendor/headroom/crates/**`) 수정 시에는 위 install 명령을 다시 실행해야 한다 (maturin 빌드, 수 분 소요).

## upstream 업데이트

```bash
git subtree pull --prefix=vendor/headroom https://github.com/headroomlabs-ai/headroom.git main --squash
```
