from dataclasses import dataclass

NO_PROPS = 8
# Nazione,Lega,Data,Ora,Match,1,X,2"


@dataclass
class MatchInfo:
    nazione: str
    lega: str
    data: str
    ora: str
    match: str
    uno: str
    ix: str
    due: str


    @staticmethod
    def from_string(raw : str):
        raw = str(raw)
        splitted = list(map(lambda x: x.strip(),raw.split(',')))
        return MatchInfo(
            splitted[0],
            splitted[1],
            splitted[2],
            splitted[3],
            splitted[4],
            splitted[5],
            splitted[6],
            splitted[7],
        )
    
    def __str__(self) -> str:
        return f"{self.nazione},{self.lega},{self.data},{self.ora},{self.match},{self.uno},{self.ix},{self.due}"
    
    def readable(self) -> list[str]:
        return [
            f"Alle ore: {self.ora.replace('.', 'e').replace('e00','')}, ci sarà: {self.match}",
            f"L'uno è quotato: {self.uno.replace('.', 'e').replace('e00','')}",
            f"Il pareggio è quotato: {self.ix.replace('.', 'e').replace('e00','')}",
            f"Il due è quotato: {self.due.replace('.', 'e').replace('e00','')}",
        ]