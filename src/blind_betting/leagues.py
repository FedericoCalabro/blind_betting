import re

from blind_betting.models import Match

COUNTRIES = {
    "ITA": "Italia",
    "INT": "Internazionale",
    "ENG": "Regno Unito",
    "ESP": "Spagna",
    "GER": "Germania",
    "FRA": "Francia",
    "NED": "Olanda",
    "POR": "Portogallo",
    "BEL": "Belgio",
    "CZE": "Repubblica Ceca",
    "GRE": "Grecia",
    "TUR": "Turchia",
}

EXCLUDED_LEAGUES = {
    "Serie D",
    "III Divisione",
    "IV Divisione",
    "V Divisione",
    "VI Divisione",
    "VII Divisione",
    "National League",
    "3. Liga",
    "2. Lig",
    "Segunda B",
    "Liga Adelante",
    "Tweede Klasse",
    "Topklasse",
    "Ceskae Moravskos Liga",
    "Football League",
}

YOUTH_WOMEN_FRIENDLIES = re.compile(r"\bU\d{2}\b|Primavera|Femminile| F$|^Amichevoli Club")


def is_wanted(match: Match) -> bool:
    return (
        match.country in COUNTRIES
        and match.league not in EXCLUDED_LEAGUES
        and not YOUTH_WOMEN_FRIENDLIES.search(match.league)
    )
