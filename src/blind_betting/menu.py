from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime

from blind_betting import speech
from blind_betting.leagues import COUNTRIES, is_wanted
from blind_betting.models import Match

CAP = 10
FAVOURITE_BANDS = ((0.0, 1.30), (1.30, 1.60), (1.60, 2.00))
SIDES = (("1", "uno"), ("2", "due"))


@dataclass
class Node:
    label: str
    details: str = ""
    children: list["Node"] = field(default_factory=list)
    match: Match | None = None

    def matches(self) -> list[Match]:
        if self.match is not None:
            return [self.match]
        found = {id(match): match for child in self.children for match in child.matches()}
        return list(found.values())


def _upcoming(matches: Iterable[Match], now: datetime) -> list[Match]:
    return sorted(
        (
            m
            for m in matches
            if is_wanted(m) and m.kickoff.date() == now.date() and m.kickoff >= now
        ),
        key=lambda m: m.kickoff,
    )


def build_menu(matches: list[Match], now: datetime) -> Node:
    today = _upcoming(matches, now)
    return _list(
        speech.MAIN_MENU,
        [
            _list("Prossime partite", [_match(m, speech.timed(m)) for m in today[:CAP]]),
            _list("Favorite", [_favourites(today, low, high) for low, high in FAVOURITE_BANDS]),
            _list(
                "Goal",
                [
                    _list("Tanti goal", _cheapest(today, "O2.5", "over")),
                    _list("Pochi goal", _cheapest(today, "U2.5", "under")),
                ],
            ),
            _list("Campionati", _countries(today, matches)),
        ],
    )


def _list(label: str, children: list[Node]) -> Node:
    children = [child for child in children if child.match is not None or child.children]
    node = Node(label, children=children)
    node.details = speech.matches(len(node.matches()))
    return node


def _match(match: Match, label: str) -> Node:
    markets = [Node(name, text) for name, text in speech.markets(match)]
    return Node(label, speech.details(match), markets, match)


def _favourites(matches: list[Match], low: float, high: float) -> Node:
    picks = []
    for match in matches:
        sides = [(match.odds[key], name) for key, name in SIDES if key in match.odds]
        if not sides:
            continue
        odd, name = min(sides)
        if low < odd <= high:
            picks.append((odd, name, match))
    picks.sort(key=lambda pick: pick[0])
    nodes = [_match(match, speech.priced(match, name, odd)) for odd, name, match in picks[:CAP]]
    return _list(speech.band(low, high), nodes)


def _cheapest(matches: list[Match], key: str, outcome: str) -> list[Node]:
    priced = sorted((m for m in matches if key in m.odds), key=lambda m: m.odds[key])
    return [_match(m, speech.priced(m, outcome, m.odds[key])) for m in priced[:CAP]]


def _countries(today: list[Match], everything: list[Match]) -> list[Node]:
    leagues: dict[str, dict[str, list[Node]]] = {code: {} for code in COUNTRIES}
    for match in everything:
        if match.country in leagues:
            leagues[match.country].setdefault(match.league, [])
    for match in today:
        leagues[match.country][match.league].append(_match(match, speech.timed(match)))
    return [
        _list(COUNTRIES[code], [_list(league, nodes) for league, nodes in by_league.items()])
        for code, by_league in leagues.items()
    ]
