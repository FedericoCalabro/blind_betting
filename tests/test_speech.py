from datetime import datetime

import pytest
from conftest import find, make_match

from blind_betting import speech


@pytest.mark.parametrize(
    ("value", "spoken"),
    [(1.13, "1 e 13"), (1.05, "1 e 05"), (2.0, "2"), (12.5, "12 e 50"), (22.0, "22")],
)
def test_numbers(value, spoken):
    assert speech.number(value) == spoken


@pytest.mark.parametrize(
    ("hour", "minute", "spoken"), [(18, 30, "18 e 30"), (16, 0, "16"), (1, 5, "1 e 05")]
)
def test_clock(hour, minute, spoken):
    assert speech.clock(datetime(2026, 10, 2, hour, minute)) == spoken


def test_counts():
    assert speech.matches(1) == "1 partita"
    assert speech.today(11) == "11 partite oggi."


def test_match_details_and_markets(schedule):
    match = find(schedule, "Kazakistan")

    assert speech.details(match) == (
        "Nations League, ore 16. Uno 1 e 85, pareggio 3 e 25, due 4 e 50."
    )
    assert speech.markets(match) == [
        ("Doppia chance", "Uno ics 1 e 17, ics due 1 e 90, uno due 1 e 33."),
        ("Under over", "Underino 2 e 60, overino 1 e 42. Under 1 e 57, over 2 e 25."),
        ("Goal no goal", "Goal 2, no goal 1 e 72."),
        ("Segna goal", "Kazakistan sì 1 e 19, no 3 e 80. Moldova sì 1 e 60, no 2 e 10."),
    ]


def test_skips_what_sisal_leaves_empty():
    match = make_match(one=1.5, two=6.0, over=1.9, NG=1.7)

    assert speech.details(match) == "Serie A, ore 18. Uno 1 e 50, due 6."
    assert speech.markets(match) == [
        ("Under over", "Over 1 e 90."),
        ("Goal no goal", "No goal 1 e 70."),
    ]
    assert speech.details(make_match()) == "Serie A, ore 18."
