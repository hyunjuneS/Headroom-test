"""[custom] tiktoken vocab 다운로드 실패(SSL/프록시 차단) 시 추정치로 폴백하는지 확인."""

import pytest

from headroom.tokenizers import tiktoken_counter as tc


def test_download_error_becomes_tiktoken_load_error(monkeypatch):
    import tiktoken

    def boom(name):
        raise OSError("SSL: CERTIFICATE_VERIFY_FAILED")

    monkeypatch.setattr(tiktoken, "get_encoding", boom)
    tc._get_encoding.cache_clear()
    tc._load_failed.discard("fake_enc")

    with pytest.raises(tc.TiktokenLoadError):
        tc.load_encoding("fake_enc")
    # 두 번째 호출은 네트워크를 다시 타지 않고 바로 실패해야 한다.
    tc._get_encoding.cache_clear()
    with pytest.raises(tc.TiktokenLoadError):
        tc.load_encoding("fake_enc")
