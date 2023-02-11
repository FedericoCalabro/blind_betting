import pandas as pd
from match_info import MatchInfo
from saver import SAVE_PATH
from constants import CSV
from pprint import pprint

class QueryMaster:
    def __init__(self, debug = False):
        self.debug = debug
        self.df = pd.read_csv(SAVE_PATH, dtype=str)

    def search(self, query, df = None) -> pd.DataFrame:
        df = self.__get_df(df)
        queried = df.query(query)
        self.__debug(f"query: '{query}'", queried)
        return queried
    
    def searchOnColumn(self, col, op, value, df = None) -> pd.DataFrame:
        QUERY = f"{col} {op} '{value}'"
        return self.search(QUERY, df)
    
    def searchByNazione(self, nazione, df = None):
        return self.searchOnColumn(CSV.NAZIONE, '==', nazione, df)
    
    def searchByLega(self, lega, df = None):
        return self.searchOnColumn(CSV.LEGA, '==', lega, df)
    
    def uniques_of_col(self, col, df = None) -> list[str]:
        df = self.__get_df(df)
        return df[col].unique().tolist()
    
    @staticmethod
    def df_to_matches(df : pd.DataFrame) -> list[MatchInfo]:
        matches = []
        for match in df.values.tolist():
            stringed = f"{','.join(match)}"
            matches.append(MatchInfo.from_string(stringed))
        return matches
    
    def __debug(self, message, df = None):
        if self.debug:
            print(f"debugger: {message}")
            if df is not None:
                for match in QueryMaster.df_to_matches(df):
                    pprint(match)

    def __get_df(self, df = None) -> pd.DataFrame:
        if df is not None:
            return df
        return self.df

