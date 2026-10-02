from datetime import datetime

import pytest
from conftest import find

from blind_betting.parser import HANDICAP, ParseError, parse_schedule


def test_reads_the_footer_and_every_match(schedule):
    assert schedule.updated == datetime(2026, 10, 2, 10, 7)
    assert len(schedule.matches) == 102


def test_reads_every_market_of_a_full_row(schedule):
    match = find(schedule, "Kazakistan")

    assert (match.country, match.league, match.away) == ("INT", "Nations League", "Moldova")
    assert match.kickoff == datetime(2026, 10, 2, 16, 0)
    assert match.odds == {
        "1": 1.85, "X": 3.25, "2": 4.5,
        "1X": 1.17, "X2": 1.9, "12": 1.33,
        "U1.5": 2.6, "O1.5": 1.42, "U2.5": 1.57, "O2.5": 2.25, "U3.5": 1.18, "O3.5": 4.0,
        "GG": 2.0, "NG": 1.72,
        "home_yes": 1.19, "home_no": 3.8, "away_yes": 1.6, "away_no": 2.1,
    }  # fmt: skip


def test_splits_two_digit_odds_that_run_into_the_next_cell(schedule):
    match = find(schedule, "Bielorussia")

    assert (match.odds["X"], match.odds["2"]) == (12.0, 22.0)
    assert "1X" not in match.odds
    assert "home_yes" not in match.odds


def test_splits_teams_with_several_words(schedule):
    pairs = {(m.home, m.away) for m in schedule.matches}

    assert ("Bosnia Erzegovina", "Svezia") in pairs
    assert ("Ucraina", "Irlanda Del Nord") in pairs


def test_keeps_the_league_across_pages(schedule):
    match = find(schedule, "Saint-Étienne")

    assert (match.country, match.league) == ("FRA", "Ligue 2")


def test_drops_the_handicap(schedule):
    assert not any(HANDICAP & match.odds.keys() for match in schedule.matches)


def test_rejects_a_pdf_that_is_not_a_schedule(tmp_path):
    blank = tmp_path / "blank.pdf"
    blank.write_bytes(
        b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 595 842]>>endobj\n"
        b"trailer<</Root 1 0 R>>\n%%EOF\n"
    )

    with pytest.raises(ParseError):
        parse_schedule(blank)
