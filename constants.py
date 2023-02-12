class Constants:

    countrycodes_dict = {
        "INT": "Internazionale",
        "ITA": "Italia",
        "ESP": "Spagna",
        "GER": "Germania",
        "FRA": "Francia",
        "NED": "Olanda",
        "ENG": "Regno Unito", 
        "POR": "Portogallo",
        "BEL": "Belgio",
        "CZE": "Repubblica Ceca",
        "GRE": "Grecia",
        "TUR": "Turchia",
        "OTH": "Altro"
    }

    allowed_countries = [
        "Internazionale", 
        "Italia",
        "Spagna",
        "Germania",
        "Francia",
        "Olanda",
        "Regno Unito",
        "Portogallo",
        "Belgio",
        "Repubblica Ceca",
        "Grecia",
        "Turchia",
        # "Altro",
    ]

    forbidden_leagues = [
        "V Divisione",
        "Serie D",
        "Primavera",
        "Serie A Femminile",
        "III Divisione",
        "IV Divisione",
        "Bundesliga F",
        "3. Liga",
        "2. Lig",
        "Segunda B",
        "Liga Adelante",
        "VII Divisione",
        "VI Divisione",
        'I Divisione F',
        'Tweede Klasse',
    ]


class CSV:
    NAZIONE = "Nazione"
    LEGA = "Lega"
    DATA = "Data"
    ORA = "Ora"
    MATCH = "Match"
    UNO = "Uno"
    IX = "Ix"
    DUE = "Due"