import logging
from datetime import date
from pathlib import Path

from curl_cffi import requests
from platformdirs import user_cache_path

URL = "https://landing.sisal.it/volantini/Scommesse_Sport/Quote/calcio%20base%20per%20manifestazione.pdf"

log = logging.getLogger(__name__)


class FetchError(Exception):
    pass


def default_path() -> Path:
    return user_cache_path("blind-betting", appauthor=False) / "palinsesto.pdf"


def fetch(path: Path | None = None) -> Path:
    path = path or default_path()
    try:
        # Sisal drops connections whose TLS fingerprint isn't a real browser's.
        response = requests.get(URL, impersonate="chrome", timeout=60)
        response.raise_for_status()
        if not response.content.startswith(b"%PDF"):
            raise FetchError(f"{URL} did not return a PDF")
        path.parent.mkdir(parents=True, exist_ok=True)
        partial = path.with_suffix(".part")
        partial.write_bytes(response.content)
        partial.replace(path)
        return path
    except (requests.RequestsError, FetchError) as exc:
        if path.exists() and date.fromtimestamp(path.stat().st_mtime) == date.today():
            log.warning("Download failed (%s), using today's copy %s", exc, path)
            return path
        raise FetchError(str(exc)) from exc
