from grouper import Grouper
from match_info import MatchInfo
from speaker import Speaker
from pynput.keyboard import Listener, Key
from pprint import pprint

class Controller:
    def __init__(self, grouper: Grouper, speaker: Speaker):
        self.grouper = grouper
        self.speaker = speaker
        self.history_dict = []
        self.history_selection = []
        self.speaker.start()
        self.start()

    def start(self):
        self.listener = Listener(on_press=self.__on_press)
        self.listener.start()
        self.history_dict.append(self.grouper.dict)
        self.history_selection.append(self.__get_current_options()[0])
        self.speaker.speak([self.history_selection[-1]])

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
        if len(self.history_dict) > 1:
            self.history_dict.pop()
            self.history_selection.pop()
            self.speaker.speak([*self.__get_to_speak(space=False)])
        else:
            self.speaker.speak(["Non puoi andare a sinistra, non c'è niente prima"])

    def __on_Key_right(self):
        next_key = self.history_selection[-1]
        curr_dict = self.history_dict[-1]
        next_val = curr_dict[next_key]
        if isinstance(next_val, dict):
            self.history_dict.append(next_val)
            self.history_selection.append(self.__get_current_options()[0])
            self.speaker.speak([*self.__get_to_speak(space=False)])
        else:
            self.speaker.speak(["Non puoi andare a destra, non c'è niente dopo"])


    def __on_Key_up(self):
        self.history_selection[-1] = self.__get_prev()
        self.speaker.speak(self.__get_to_speak(space=False))

    def __on_Key_down(self):
        self.history_selection[-1] = self.__get_next()
        self.speaker.speak(self.__get_to_speak(space=False))

    def __on_Key_space(self):
        self.speaker.speak(self.__get_to_speak(space=True))

    def __get_next(self) -> str | MatchInfo:
        current_options = self.__get_current_options()
        idx = current_options.index(self.history_selection[-1])
        return current_options[(idx + 1) % len(current_options)]
    
    def __get_prev(self) -> str | MatchInfo:
        current_options = self.__get_current_options()
        idx = current_options.index(self.history_selection[-1])
        return current_options[(idx - 1) % len(current_options)]
    
    def __get_to_speak(self, space : bool) -> list[str]:
        current_selection = self.history_selection[-1]
        current_dict = self.history_dict[-1]
        next_value = current_dict[current_selection]
        if isinstance(next_value, MatchInfo):
            if space==True:
                return next_value.readable()
        return [current_selection]
    
    def __get_current_options(self):
        return list(self.history_dict[-1].keys())
    
    
