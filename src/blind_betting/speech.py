from datetime import datetime

from blind_betting.models import Match

MAIN_MENU = "Menu principale"
WAIT = "Un momento."
NO_MATCHES = "Nessuna partita oggi."
UNAVAILABLE = "Palinsesto non disponibile, riprova più tardi."


def number(value: float) -> str:
    whole, cents = f"{value:.2f}".split(".")
    return whole if cents == "00" else f"{whole} e {cents}"


def clock(moment: datetime) -> str:
    return f"{moment.hour}" if moment.minute == 0 else f"{moment.hour} e {moment.minute:02d}"


def matches(count: int) -> str:
    return "1 partita" if count == 1 else f"{count} partite"


def today(count: int) -> str:
    return f"{matches(count)} oggi."


def timed(match: Match) -> str:
    return f"{clock(match.kickoff)}, {match.teams}"


def priced(match: Match, outcome: str, odd: float) -> str:
    return f"{match.teams}, {outcome} {number(odd)}"


def band(low: float, high: float) -> str:
    return f"fino a {number(high)}" if low == 0 else f"da {number(low)} a {number(high)}"


def details(match: Match) -> str:
    odds = _odds(match, ("uno", "1"), ("pareggio", "X"), ("due", "2"))
    return " ".join(filter(None, (f"{match.league}, ore {clock(match.kickoff)}.", _sentence(odds))))


def markets(match: Match) -> list[tuple[str, str]]:
    found = [
        ("Doppia chance", [_odds(match, ("uno ics", "1X"), ("ics due", "X2"), ("uno due", "12"))]),
        (
            "Under over",
            [
                _odds(match, ("underino", "U1.5"), ("overino", "O1.5")),
                _odds(match, ("under", "U2.5"), ("over", "O2.5")),
            ],
        ),
        ("Goal no goal", [_odds(match, ("goal", "GG"), ("no goal", "NG"))]),
        ("Segna goal", [_scores(match.home, match, "home"), _scores(match.away, match, "away")]),
    ]
    spoken = [
        (name, " ".join(_sentence(clause) for clause in clauses if clause))
        for name, clauses in found
    ]
    return [(name, text) for name, text in spoken if text]


def _scores(team: str, match: Match, side: str) -> str:
    odds = _odds(match, ("sì", f"{side}_yes"), ("no", f"{side}_no"))
    return f"{team} {odds}" if odds else ""


def _sentence(text: str) -> str:
    return f"{text[:1].upper()}{text[1:]}." if text else ""


def _odds(match: Match, *outcomes: tuple[str, str]) -> str:
    return ", ".join(
        f"{name} {number(match.odds[key])}" for name, key in outcomes if key in match.odds
    )
