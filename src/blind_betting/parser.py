import re
from datetime import datetime
from pathlib import Path

import pdfplumber

from blind_betting.models import Match, Schedule

HEADER = ("1", "X", "2", "H", "1", "X", "2", "1X", "X2", "12", "U", "O", "U", "O", "U", "O")
HEADER += ("G", "NG", "SI", "NO", "SI", "NO")
COLUMNS = ("1", "X", "2", "H", "H1", "HX", "H2", "1X", "X2", "12", "U1.5", "O1.5", "U2.5")
COLUMNS += ("O2.5", "U3.5", "O3.5", "GG", "NG", "home_yes", "home_no", "away_yes", "away_no")
HANDICAP = {"H", "H1", "HX", "H2"}

DATE = re.compile(r"(\d{1,2})/(\d{1,2})")
TIME = re.compile(r"(\d{1,2})\.(\d{2})")
COUNTRY = re.compile(r"[A-Z]{3}")
NUMBER = re.compile(r"\d+,\d{2}|-?\d+")
UPDATED = re.compile(r"Dati aggiornati al (\d{2}/\d{2}/\d{4}) - ore (\d{2}:\d{2})")


class ParseError(Exception):
    pass


def parse_schedule(path: Path) -> Schedule:
    with pdfplumber.open(path) as pdf:
        pages = [
            _lines(page.extract_words(x_tolerance=1.5, return_chars=True)) for page in pdf.pages
        ]
    updated = _updated(pages)
    matches: list[Match] = []
    league: tuple[str, str] | None = None
    for lines in pages:
        layout = _Layout.find(lines)
        if layout is None:
            continue
        for line in lines[layout.row + 1 :]:
            first = line[0]["text"]
            if DATE.fullmatch(first) and len(line) > 1 and TIME.match(line[1]["text"]):
                if league is not None:
                    matches.append(layout.match(line, league, updated))
            elif COUNTRY.fullmatch(first) and len(line) > 1 and line[0]["x0"] < layout.teams_x:
                league = (first, " ".join(word["text"] for word in line[1:]))
    if not matches:
        raise ParseError("no matches found: is this a Sisal 'calcio per manifestazione' PDF?")
    return Schedule(updated, matches)


def _lines(words: list[dict]) -> list[list[dict]]:
    lines: list[list[dict]] = []
    top = None
    for word in sorted(words, key=_middle):
        if top is None or _middle(word) - top > 4:
            lines.append([])
            top = _middle(word)
        lines[-1].append(word)
    return [sorted(line, key=lambda word: word["x0"]) for line in lines]


def _middle(word: dict) -> float:
    return (word["top"] + word["bottom"]) / 2


def _updated(pages: list[list[list[dict]]]) -> datetime:
    for lines in pages:
        for line in lines:
            if found := UPDATED.search(" ".join(word["text"] for word in line)):
                return datetime.strptime(" ".join(found.groups()), "%d/%m/%Y %H:%M")
    raise ParseError("no 'Dati aggiornati al' footer found")


class _Layout:
    def __init__(self, row: int, line: list[dict], odds: list[dict]):
        self.row = row
        squadre = [word for word in line if word["text"] == "Squadra"]
        self.teams_x = squadre[0]["x0"] - 2
        self.away_x = squadre[1]["x0"] - 2
        self.centres = [(word["x0"] + word["x1"]) / 2 for word in odds]
        self.half_gap = (self.centres[1] - self.centres[0]) / 2
        self.odds_x = self.centres[0] - self.half_gap

    @classmethod
    def find(cls, lines: list[list[dict]]) -> "_Layout | None":
        for row, line in enumerate(lines):
            texts = [word["text"] for word in line]
            if texts[:2] != ["Data", "Ora"] or texts.count("Squadra") != 2:
                continue
            after = texts.index("Squadra", texts.index("Squadra") + 1) + 2
            odds = [word for word in line[after:] if word["text"] in HEADER]
            if tuple(word["text"] for word in odds) != HEADER:
                raise ParseError(f"unexpected odds columns: {' '.join(texts[after:])}")
            return cls(row, line, odds)
        return None

    def match(self, line: list[dict], league: tuple[str, str], updated: datetime) -> Match:
        day, month = (int(part) for part in DATE.fullmatch(line[0]["text"]).groups())
        hour, minute = (int(part) for part in TIME.match(line[1]["text"]).groups())
        year = updated.year + (month < updated.month)
        return Match(
            country=league[0],
            league=league[1],
            kickoff=datetime(year, month, day, hour, minute),
            home=self._words(line, self.teams_x, self.away_x),
            away=self._words(line, self.away_x, self.odds_x),
            odds=self._odds(line),
        )

    @staticmethod
    def _words(line: list[dict], start: float, end: float) -> str:
        return " ".join(word["text"] for word in line if start <= word["x0"] < end)

    def _odds(self, line: list[dict]) -> dict[str, float]:
        odds = {}
        for word in line:
            if word["x0"] < self.odds_x:
                continue
            # Two-digit odds overflow into the next cell ("12,0022,00"), so place each number
            # by its own characters rather than by the word.
            for found in NUMBER.finditer(word["text"]):
                chars = word["chars"][found.start() : found.end()]
                centre = (chars[0]["x0"] + chars[-1]["x1"]) / 2
                column = min(range(len(self.centres)), key=lambda i: abs(self.centres[i] - centre))
                key = COLUMNS[column]
                if abs(self.centres[column] - centre) <= self.half_gap and key not in HANDICAP:
                    odds[key] = float(found.group().replace(",", "."))
        return odds
