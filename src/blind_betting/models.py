from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Match:
    country: str
    league: str
    kickoff: datetime
    home: str
    away: str
    odds: dict[str, float] = field(default_factory=dict)

    @property
    def teams(self) -> str:
        return f"{self.home} - {self.away}"


@dataclass
class Schedule:
    updated: datetime
    matches: list[Match]
