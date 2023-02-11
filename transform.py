from reader import PalinsestoPdfReader
from constants import Constants
from match_info import NO_PROPS
import re

class PalinsestoTransformer:
    def __init__(self, reader : PalinsestoPdfReader):
        self.data = []
        self.__manifestazione = ""
        for line in reader.data:
            self.__line = line.strip()
            self.__update_manifestazione()
            if(self.__should_add()):
                self.__transform_line()
                if self.__can_add():
                    self.data.append(self.__line)

    def __should_add(self): 
        regex = r"^[a-zA-Z].*$"
        return re.search(regex, self.__line) is None
    
    def __transform_line(self):
        self.__remove_after_main_quotes()
        self.__remove_between_date_and_match()
        self.__sub_re_with_csv_like(r"\d{1,2}/\d{1,2}")
        self.__sub_re_with_csv_like(r"\d{2}\.\d{2}")
        self.__sub_re_with_csv_like(r"[a-zA-Z].*?(?=\s\d+\,\d{2})")
        self.__main_quotes_csv_like()
        self.__add_country_and_division()
        self.__line = self.__line.replace('�','')
    
    def __can_add(self):
        return len(self.__line.split(',')) == NO_PROPS
    
    def __remove_after_main_quotes(self):
        regex = r"^\d.*?[a-zA-Z][0-9a-zA-Z_.� ]+\s\d+[, ]\d{2}\s*\d+[, ]\d{2}\s*\d+[, ]\d{2}"
        match = re.search(regex, self.__line)
        if(match is not None):
            self.__line = self.__line[:match.span()[1]] 

    def __remove_between_date_and_match(self):
        regex = r"(?<=\.\d{2}).*?(?=[a-zA-Z])"
        match = re.search(regex, self.__line)
        if(match is not None):
            self.__line = re.sub(regex, " ", self.__line)

    def __add_country_and_division(self):
        splitted = self.__manifestazione.split(" ")
        country_code = splitted[0]
        division = " ".join(splitted[1:])
        self.__line = f"{Constants.countrycodes_dict.get(country_code, 'Altro')}, {division}, {self.__line}"

    def __sub_re_with_csv_like(self, regex):
        match = re.search(regex, self.__line)
        if match is not None:
            self.__line = re.sub(regex, f"{match.group()},", self.__line)

    def __main_quotes_csv_like(self):
        regex = r"(\d+,\d{2})\s*(\d+,\d{2})\s*(\d+,\d{2})"
        match = re.search(regex, self.__line)
        if match is not None:
            new = f"{match.group(1).replace(',', '.')}, {match.group(2).replace(',', '.')}, {match.group(3).replace(',', '.')}"
            self.__line = re.sub(regex, new, self.__line)

    def __update_manifestazione(self):
        regex = r"^([a-zA-Z].*)"
        match = re.search(regex, self.__line)
        if(match is not None):
            self.__manifestazione = match.groups()[0]