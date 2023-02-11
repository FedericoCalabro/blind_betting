from transform import PalinsestoTransformer
from match_info import MatchInfo
from constants import Constants
from datetime import date
from constants import CSV

SAVE_PATH = "palinsesto.csv"


class PalinsestoSaver:
    def __init__(self, transformer: PalinsestoTransformer):
        today = date.today().strftime(' %d %m').replace(' 0', ' ').strip().replace(' ','/')
        data_model = map(lambda x: MatchInfo.from_string(x), transformer.data)
        data_model = filter(lambda x: x.data == today, data_model)
        data_model = filter(lambda x: x.nazione in Constants.allowed_countries, data_model)
        data_model = filter(lambda x: x.lega not in Constants.forbidden_leagues, data_model)
        data_model = sorted(data_model, key=lambda x: x.nazione)
        self.data = [f"{CSV.NAZIONE},{CSV.LEGA},{CSV.DATA},{CSV.ORA},{CSV.MATCH},{CSV.UNO},{CSV.IX},{CSV.DUE}"]
        self.data.extend(map(lambda x: str(x), data_model))
        file = open(SAVE_PATH, 'w', encoding='utf-8')
        file.write("\n".join(self.data))