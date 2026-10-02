from blind_betting.menu import Node
from blind_betting.navigator import Navigator


def menu() -> Node:
    market = Node("Doppia chance", "Uno ics 1 e 10.")
    first = Node("18, Inter - Parma", "Serie A, ore 18.", [market])
    second = Node("20, Milan - Roma", "Serie A, ore 20.")
    return Node(
        "Menu principale",
        children=[
            Node("Prossime partite", "2 partite", [first, second]),
            Node("Favorite", "1 partita", [Node("fino a 1 e 30", "1 partita", [first])]),
        ],
    )


def test_up_and_down_wrap_around():
    nav = Navigator(menu())

    assert nav.down() == "Favorite"
    assert nav.down() == "Prossime partite"
    assert nav.up() == "Favorite"


def test_right_goes_in_and_left_comes_back():
    nav = Navigator(menu())

    assert nav.right() == "18, Inter - Parma"
    assert nav.down() == "20, Milan - Roma"
    assert nav.left() == "Prossime partite"
    assert nav.left() == "Menu principale"
    assert nav.right() == "18, Inter - Parma"


def test_space_says_the_details():
    nav = Navigator(menu())

    assert nav.space() == "2 partite"
    nav.right()
    assert nav.space() == "Serie A, ore 18."


def test_right_on_a_leaf_says_its_details():
    nav = Navigator(menu())
    nav.right()

    assert nav.right() == "Doppia chance"
    assert nav.right() == "Uno ics 1 e 10."
    assert nav.space() == "Uno ics 1 e 10."
    assert nav.left() == "18, Inter - Parma"
