from grouper import Grouper
from match_info import MatchInfo
from speaker import Speaker
from pynput.keyboard import Listener, Key, KeyCode
from enum import Enum


class Menu(Enum):
    UNITIALIZED = ""
    NAZIONE = "PAGINA NAZIONI"
    LEGA = "PAGINA LEGHE"
    MATCH = "PAGINA PARTITE"


class Controller:
    def __init__(self, grouper: Grouper, speaker: Speaker):
        self.grouper = grouper
        self.speaker = speaker
        self.current_menu = Menu.UNITIALIZED
        self.current_selection : str | MatchInfo | None = None
        self.current_nazione : str | None = None
        self.current_lega : str | None = None
        self.current_match : MatchInfo | None = None
        self.current_options = []
        self.start()

    def start(self):
        nazioni = self.grouper.get_nazioni()
        if len(nazioni) == 0:
            self.speaker.speak(['Oggi non ci sono partite'])
        else:
            self.listener = Listener(on_press=self.__on_press)
            self.listener.start()
            self.current_menu = Menu.NAZIONE
            self.current_options = nazioni
            self.current_nazione = nazioni[0]
            self.current_selection = self.current_nazione
            self.speaker.speak([Menu.NAZIONE.value, self.current_selection])

    def __on_press(self, key):
        if key == Key.esc:
            self.__on_Key_esc()
        elif key == Key.left:
          self.__on_Key_left()
        elif key == Key.up:
          self.__on_Key_up()
        elif key == Key.right:
          self.__on_Key_right()
        elif key == Key.down:
          self.__on_Key_down()
        elif key == Key.space:
            self.__on_Key_space()

        

    def __on_Key_esc(self):
        self.listener.stop()
        self.speaker.speak(['exit'])

    def __on_Key_left(self):
        if self.current_menu == Menu.LEGA:
            nazioni = self.grouper.get_nazioni()
            self.current_options = nazioni
            self.current_lega = None
            self.current_selection = self.current_nazione
            self.current_menu = Menu.NAZIONE
        elif self.current_menu == Menu.MATCH:
            leghe = self.grouper.get_leghe(self.current_nazione)
            self.current_options = leghe
            self.current_match = None
            self.current_selection = self.current_lega
            self.current_menu = Menu.LEGA

        self.speaker.speak([str(self.current_menu.value), *self.__get_to_speak()])

    def __on_Key_up(self):
        if self.current_menu == Menu.NAZIONE:
            self.current_nazione = self.__get_prev(self.current_nazione)
            self.current_selection = self.current_nazione
        elif self.current_menu == Menu.LEGA:
            self.current_lega = self.__get_prev(self.current_lega)
            self.current_selection = self.current_lega
        elif self.current_menu == Menu.MATCH:
            self.current_match = self.__get_prev(self.current_match)
            self.current_selection = self.current_match

        self.speaker.speak(self.__get_to_speak())

    def __on_Key_right(self):
        if self.current_menu == Menu.NAZIONE:
            leghe = self.grouper.get_leghe(self.current_nazione)
            self.current_options = leghe
            self.current_lega = self.current_options[0]
            self.current_selection = self.current_lega
            self.current_menu = Menu.LEGA
        elif self.current_menu == Menu.LEGA:
            matches = self.grouper.get_matches(self.current_nazione, self.current_lega)
            self.current_options = matches
            self.current_match = self.current_options[0]
            self.current_selection = self.current_match
            self.current_menu = Menu.MATCH

        self.speaker.speak([str(self.current_menu.value), *self.__get_to_speak()])

    def __on_Key_down(self):
        if self.current_menu == Menu.NAZIONE:
            self.current_nazione = self.__get_next(self.current_nazione)
            self.current_selection = self.current_nazione
        elif self.current_menu == Menu.LEGA:
            self.current_lega = self.__get_next(self.current_lega) 
            self.current_selection = self.current_lega
        elif self.current_menu == Menu.MATCH:
            self.current_match = self.__get_next(self.current_match)
            self.current_selection = self.current_match

        self.speaker.speak(self.__get_to_speak())

    def __on_Key_space(self):
        pass

    def __get_next(self, current_selection) -> str | MatchInfo:
        idx = self.current_options.index(current_selection)
        return self.current_options[(idx + 1) % len(self.current_options)]
    
    def __get_prev(self, current_selection) -> str | MatchInfo:
        idx = self.current_options.index(current_selection)
        return self.current_options[(idx - 1) % len(self.current_options)]
    
    def __get_to_speak(self) -> list[str]:
        if isinstance(self.current_selection, MatchInfo):
            return self.current_selection.readable()
        return [str(self.current_selection)]
