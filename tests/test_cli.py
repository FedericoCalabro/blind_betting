import pytest
from conftest import FIXTURE
from typer.testing import CliRunner

from blind_betting import cli, speech
from blind_betting.sisal import FetchError

runner = CliRunner()
DAY = ["--pdf", str(FIXTURE), "--date", "2026-10-02"]


class FakeSpeaker:
    def __init__(self, rate: int):
        self.rate = rate
        self.heard: list[str] = []
        self.waited = 0
        self.closed = False

    def start(self) -> None:
        pass

    def say(self, text: str) -> None:
        self.heard.append(text)

    def wait(self) -> None:
        self.waited += 1

    def close(self) -> None:
        self.closed = True


@pytest.fixture
def speaker(monkeypatch) -> list[FakeSpeaker]:
    made: list[FakeSpeaker] = []

    def make(rate: int) -> FakeSpeaker:
        made.append(FakeSpeaker(rate))
        return made[-1]

    monkeypatch.setattr(cli, "speaker", make)
    return made


def test_lists_the_menu():
    result = runner.invoke(cli.app, [*DAY, "--list"])

    assert result.exit_code == 0, result.output
    assert "11 partite oggi. Quote aggiornate al 02/10 10:07" in result.output
    for line in ("Prossime partite", "16, Kazakistan - Moldova", "Favorite", "Campionati"):
        assert line in result.output


def test_speaks_and_follows_the_keys(monkeypatch, speaker):
    def press(navigator, say):
        for key in (navigator.right, navigator.space, navigator.right, navigator.down):
            say(key())

    monkeypatch.setattr(cli, "listen", press)

    result = runner.invoke(cli.app, [*DAY, "--rate", "150"])

    assert result.exit_code == 0, result.output
    assert speaker[0].rate == 150
    assert speaker[0].heard == [
        speech.WAIT,
        "11 partite oggi. Prossime partite",
        "16, Kazakistan - Moldova",
        "Nations League, ore 16. Uno 1 e 85, pareggio 3 e 25, due 4 e 50.",
        "Doppia chance",
        "Under over",
    ]
    assert speaker[0].closed


def test_says_when_the_schedule_is_unavailable(monkeypatch, speaker):
    def fail():
        raise FetchError("connection reset by peer")

    monkeypatch.setattr(cli, "fetch", fail)

    result = runner.invoke(cli.app, [])

    assert result.exit_code == 1
    assert speaker[0].heard[-1] == speech.UNAVAILABLE
    assert speaker[0].waited == 1


def test_says_when_there_are_no_matches(speaker):
    result = runner.invoke(cli.app, ["--pdf", str(FIXTURE), "--date", "2026-10-05"])

    assert result.exit_code == 0
    assert speaker[0].heard[-1] == speech.NO_MATCHES


def test_version():
    result = runner.invoke(cli.app, ["--version"])

    assert result.exit_code == 0
    assert result.output.startswith("blind-betting 2.0.0")
