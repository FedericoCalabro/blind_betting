from match_info import MatchInfo
from query_master import QueryMaster
from constants import CSV

class Grouper:
    def __init__(self, query_master: QueryMaster):
        self.dict = {}
        self.__master = query_master
        for nazione in self.__master.uniques_of_col(CSV.NAZIONE):
            self.dict[nazione] = {}
            df = self.__master.searchByNazione(nazione)
            for lega in self.__master.uniques_of_col(CSV.LEGA, df):
                self.dict[nazione][lega] = []
                df = self.__master.searchByLega(lega)
                matches = QueryMaster.df_to_matches(df)
                sorted(matches, key=lambda x: str(x.ora))
                for match_info in QueryMaster.df_to_matches(df):
                    self.dict[nazione][lega].append(match_info)

    def get_nazioni(self) -> list[str]:
        return list(self.dict.keys())

    def get_leghe(self, nazione) -> list[str]:
        return list(self.dict[nazione].keys())

    def get_matches(self, nazione, lega) -> list[MatchInfo]:
        return list(self.dict[nazione][lega])
