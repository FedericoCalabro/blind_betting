from blind_betting import speech
from blind_betting.menu import Node


class Navigator:
    def __init__(self, root: Node):
        self._path: list[tuple[Node, int]] = [(root, 0)]

    @property
    def current(self) -> Node:
        parent, index = self._path[-1]
        return parent.children[index]

    def up(self) -> str:
        return self._move(-1)

    def down(self) -> str:
        return self._move(1)

    def right(self) -> str:
        if not self.current.children:
            return self.space()
        self._path.append((self.current, 0))
        return self.current.label

    def left(self) -> str:
        if len(self._path) == 1:
            return speech.MAIN_MENU
        self._path.pop()
        return self.current.label

    def space(self) -> str:
        return self.current.details or self.current.label

    def _move(self, step: int) -> str:
        parent, index = self._path[-1]
        self._path[-1] = (parent, (index + step) % len(parent.children))
        return self.current.label


def listen(navigator: Navigator, on_text) -> None:
    from pynput.keyboard import Key, Listener

    actions = {
        Key.up: navigator.up,
        Key.down: navigator.down,
        Key.left: navigator.left,
        Key.right: navigator.right,
        Key.space: navigator.space,
    }

    def on_press(key) -> bool | None:
        if key == Key.esc:
            return False
        if action := actions.get(key):
            on_text(action())
        return None

    with Listener(on_press=on_press) as listener:
        listener.join()
