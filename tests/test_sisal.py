import os
import time

import pytest
from curl_cffi.requests.exceptions import ConnectionError, HTTPError

from blind_betting import sisal
from blind_betting.sisal import FetchError, fetch

PDF = b"%PDF-1.4 schedule"


class FakeResponse:
    def __init__(self, content: bytes = PDF, status: int = 200):
        self.content = content
        self.status = status

    def raise_for_status(self) -> None:
        if self.status >= 400:
            raise HTTPError(f"HTTP {self.status}")


def serve(monkeypatch, outcome) -> list[dict]:
    calls = []

    def get(url, **kwargs):
        calls.append({"url": url, **kwargs})
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    monkeypatch.setattr(sisal.requests, "get", get)
    return calls


def test_downloads_as_a_browser(monkeypatch, tmp_path):
    calls = serve(monkeypatch, FakeResponse())
    path = tmp_path / "cache" / "palinsesto.pdf"

    assert fetch(path) == path
    assert path.read_bytes() == PDF
    assert calls[0]["url"] == sisal.URL
    assert calls[0]["impersonate"] == "chrome"


def test_falls_back_to_todays_copy(monkeypatch, tmp_path):
    serve(monkeypatch, ConnectionError("connection reset by peer"))
    path = tmp_path / "palinsesto.pdf"
    path.write_bytes(PDF)

    assert fetch(path) == path


@pytest.mark.parametrize(
    "outcome",
    [
        ConnectionError("connection reset by peer"),
        FakeResponse(status=503),
        FakeResponse(b"<html>"),
    ],
)
def test_fails_without_a_copy_from_today(monkeypatch, tmp_path, outcome):
    serve(monkeypatch, outcome)
    path = tmp_path / "palinsesto.pdf"
    path.write_bytes(PDF)
    yesterday = time.time() - 86_400
    os.utime(path, (yesterday, yesterday))

    with pytest.raises(FetchError):
        fetch(path)
