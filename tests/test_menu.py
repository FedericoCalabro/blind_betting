from datetime import datetime

from conftest import make_match

from blind_betting.menu import CAP, Node, build_menu

MORNING = datetime(2026, 10, 2, 9, 0)


def labels(node: Node) -> list[str]:
    return [child.label for child in node.children]


def child(node: Node, *path: str) -> Node:
    for label in path:
        node = next(c for c in node.children if c.label == label)
    return node


def test_main_menu():
    menu = build_menu([make_match(one=1.2, two=9.0, over=1.5, under=2.4)], MORNING)

    assert labels(menu) == ["Prossime partite", "Favorite", "Goal", "Campionati"]
    assert menu.details == "1 partita"


def test_next_matches_skip_started_ones_and_other_days():
    matches = [
        make_match("Late", "B", at="2026-10-02 20:45"),
        make_match("Started", "B", at="2026-10-02 15:00"),
        make_match("Early", "B", at="2026-10-02 18:30"),
        make_match("Tomorrow", "B", at="2026-10-03 18:30"),
    ]

    menu = build_menu(matches, datetime(2026, 10, 2, 16, 0))

    assert labels(child(menu, "Prossime partite")) == ["18 e 30, Early - B", "20 e 45, Late - B"]


def test_unwanted_countries_and_leagues_are_left_out():
    matches = [
        make_match("Serie D", "B", league="Serie D"),
        make_match("Primavera", "B", league="Primavera 1"),
        make_match("Women", "B", country="GER", league="Bundesliga F"),
        make_match("Youth", "B", country="INT", league="Amichevoli U19 (Poss. Cambio Format)"),
        make_match("Boca", "River", country="ARG", league="Primera Division"),
    ]

    assert build_menu(matches, MORNING).children == []


def test_favourites_are_banded_by_the_lower_of_one_and_two_numerically():
    matches = [
        make_match("Heavy", "B", one=1.25, two=10.0),
        make_match("A", "Away", one=9.0, two=1.45),
        make_match("Close", "B", one=1.35, two=8.0),
        make_match("Even", "B", one=2.5, two=2.6),
    ]

    favourites = child(build_menu(matches, MORNING), "Favorite")

    assert labels(favourites) == ["fino a 1 e 30", "da 1 e 30 a 1 e 60"]
    assert labels(child(favourites, "fino a 1 e 30")) == ["Heavy - B, uno 1 e 25"]
    assert labels(child(favourites, "da 1 e 30 a 1 e 60")) == [
        "Close - B, uno 1 e 35",
        "A - Away, due 1 e 45",
    ]


def test_lists_keep_the_cheapest_ten():
    matches = [make_match(f"T{i}", "B", over=1.2 + i / 100) for i in range(CAP + 2)][::-1]

    many_goals = child(build_menu(matches, MORNING), "Goal", "Tanti goal")

    assert len(many_goals.children) == CAP
    assert many_goals.children[0].label == "T0 - B, over 1 e 20"
    assert many_goals.children[-1].label == "T9 - B, over 1 e 29"


def test_a_match_in_several_lists_counts_once():
    goal = child(build_menu([make_match(over=1.5, under=2.4)], MORNING), "Goal")

    assert labels(goal) == ["Tanti goal", "Pochi goal"]
    assert goal.details == "1 partita"


def test_leagues_are_grouped_by_country_in_schedule_order():
    matches = [
        make_match("Juve", "Roma", at="2026-10-02 20:45"),
        make_match("Bari", "Pisa", league="Serie B"),
        make_match("Milan", "Lazio", at="2026-10-02 18:00"),
        make_match("Arsenal", "Leeds", country="ENG", league="Premier League"),
        make_match("Inter", "Lecce", league="Supercoppa"),
        make_match("Barça", "Betis", country="ESP", league="Supercoppa"),
    ]

    leagues = child(build_menu(matches, MORNING), "Campionati")

    assert labels(leagues) == ["Italia", "Regno Unito", "Spagna"]
    assert labels(child(leagues, "Italia")) == ["Serie A", "Serie B", "Supercoppa"]
    assert labels(child(leagues, "Italia", "Serie A")) == [
        "18, Milan - Lazio",
        "20 e 45, Juve - Roma",
    ]
    assert labels(child(leagues, "Spagna", "Supercoppa")) == ["18, Barça - Betis"]
    assert child(leagues, "Italia").details == "4 partite"


def test_a_match_opens_its_markets():
    match = child(build_menu([make_match(one=1.5, GG=1.8, NG=1.9)], MORNING), "Prossime partite")

    node = match.children[0]
    assert node.details == "Serie A, ore 18. Uno 1 e 50."
    assert [(m.label, m.details) for m in node.children] == [
        ("Goal no goal", "Goal 1 e 80, no goal 1 e 90.")
    ]
