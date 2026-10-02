from datetime import datetime
from pathlib import Path

import pytest

from blind_betting.models import Match, Schedule
from blind_betting.parser import parse_schedule

FIXTURE = Path(__file__).parent / "fixtures" / "palinsesto.pdf"


def make_match(
    home: str = "Inter",
    away: str = "Parma",
    *,
    at: str = "2026-10-02 18:00",
    country: str = "ITA",
    league: str = "Serie A",
    **odds: float,
) -> Match:
    aliases = {"one": "1", "draw": "X", "two": "2", "over": "O2.5", "under": "U2.5"}
    return Match(
        country,
        league,
        datetime.fromisoformat(at),
        home,
        away,
        {aliases.get(key, key): value for key, value in odds.items()},
    )


@pytest.fixture(scope="session")
def schedule() -> Schedule:
    return parse_schedule(FIXTURE)


def find(schedule: Schedule, home: str) -> Match:
    return next(match for match in schedule.matches if match.home == home)
