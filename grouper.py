from match_info import MatchInfo
from query_master import QueryMaster
from constants import CSV

class Grouper:
    def __init__(self, query_master: QueryMaster):
        self.dict = {}
        self.__master = query_master
        self.__add_lowest_quotes_between(KEY='Cerca tra tutte le partite', min="1.10", max="1.40", n=10, casa=True, ospite=True)
        self.__add_lowest_quotes_between(KEY='Cerca tra tutte le partite', min="1.30", max="1.60", n=10, casa=True, ospite=True)
        self.__add_lowest_quotes_between(KEY='Cerca tra tutte le partite', min="1.50", max="1.80", n=10, casa=True, ospite=True)
        self.__add_lowest_quotes_between(KEY='Cerca tra tutte le partite', min="1.80", max="999", n=10, casa=True, ospite=True)
        
        self.__add_lowest_quotes_between(KEY='Cerca tra le partite in casa', min="1.10", max="1.40", n=10, casa=True, ospite=False)
        self.__add_lowest_quotes_between(KEY='Cerca tra le partite in casa', min="1.30", max="1.60", n=10, casa=True, ospite=False)
        self.__add_lowest_quotes_between(KEY='Cerca tra le partite in casa', min="1.50", max="1.80", n=10, casa=True, ospite=False)
        self.__add_lowest_quotes_between(KEY='Cerca tra le partite in casa', min="1.80", max="999", n=10, casa=True, ospite=False)
        
        self.__add_lowest_quotes_between(KEY='Cerca tra le partite fuori casa', min="1.10", max="1.40", n=10, casa=False, ospite=True)
        self.__add_lowest_quotes_between(KEY='Cerca tra le partite fuori casa', min="1.30", max="1.60", n=10, casa=False, ospite=True)
        self.__add_lowest_quotes_between(KEY='Cerca tra le partite fuori casa', min="1.50", max="1.80", n=10, casa=False, ospite=True)
        self.__add_lowest_quotes_between(KEY='Cerca tra le partite fuori casa', min="1.80", max="999", n=10, casa=False, ospite=True)

        self.__add_palinsesto(KEY="Palinsesto")


    def get_nazioni(self) -> list[str]:
        return list(self.dict.keys())

    def get_leghe(self, nazione) -> list[str]:
        return list(self.dict[nazione].keys())

    def get_matches(self, nazione, lega) -> list[MatchInfo]:
        return list(self.dict[nazione][lega])
    
    def __add_lowest_quotes_between(self, KEY : str, min : str, max : str, n : int, casa : bool, ospite : bool):

        df = self.__master.matches_with_quotes_between(float(min), float(max), casa, ospite)
        matches = QueryMaster.df_to_matches(df)[:n]

        if len(matches) <= 0:
            return

        if not KEY in self.dict:
            self.dict[KEY] = {}

        s_min = str(min).replace('.', 'e').replace('e00','')
        s_max = str(max).replace('.', 'e').replace('e00','')

        if float(max) >= 99:
            key_to_add = f"quota superiore a {s_min}"
        else:
            key_to_add = f"quota compresa tra {s_min} e {s_max}"

        self.dict[KEY][key_to_add] = {}

        for match_info in QueryMaster.df_to_matches(df)[:n]:
            self.dict[KEY][key_to_add][match_info.match] = match_info


    def __add_palinsesto(self, KEY : str):
        self.dict[KEY] = {}
        for nazione in self.__master.uniques_of_col(CSV.NAZIONE):
            self.dict[KEY][nazione] = {}
            df = self.__master.searchByNazione(nazione)
            for lega in self.__master.uniques_of_col(CSV.LEGA, df):
                self.dict[KEY][nazione][lega] = {}
                df = self.__master.searchByLega(lega)
                matches = QueryMaster.df_to_matches(df)
                sorted(matches, key=lambda x: str(x.ora))
                for match_info in QueryMaster.df_to_matches(df):
                    self.dict[KEY][nazione][lega][match_info.match] = match_info