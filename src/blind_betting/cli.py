import logging
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.markup import escape
from rich.tree import Tree

from blind_betting import __version__, speech
from blind_betting.menu import Node, build_menu
from blind_betting.navigator import Navigator, listen
from blind_betting.parser import ParseError, parse_schedule
from blind_betting.sisal import FetchError, fetch
from blind_betting.voice import Speaker, speaker

console = Console()
log = logging.getLogger("blind_betting")

app = typer.Typer(
    help="Read Sisal's football odds aloud and browse them with the arrow keys.",
    add_completion=False,
)


class Announcer:
    def __init__(self, voice: Speaker | None):
        self.voice = voice

    def __call__(self, text: str, *, wait: bool = False) -> None:
        if self.voice is None:
            return
        console.print(escape(text))
        self.voice.say(text)
        if wait:
            self.voice.wait()


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"blind-betting {__version__}")
        raise typer.Exit


def _tree(node: Node, tree: Tree) -> Tree:
    for child in node.children:
        if child.match is not None:
            tree.add(f"{escape(child.label)}  [dim]{escape(child.details)}[/]")
        else:
            _tree(child, tree.add(f"[bold]{escape(child.label)}[/] [dim]({child.details})[/]"))
    return tree


@app.command()
def main(
    pdf: Annotated[
        Path | None,
        typer.Option(
            exists=True, dir_okay=False, help="Read this PDF instead of downloading today's."
        ),
    ] = None,
    day: Annotated[
        datetime | None,
        typer.Option(
            "--date",
            formats=["%Y-%m-%d"],
            help="Show this whole day instead of what is left of today.",
            show_default=False,
        ),
    ] = None,
    rate: Annotated[int, typer.Option(min=50, max=400, help="Speech speed, words a minute.")] = 125,
    show: Annotated[
        bool, typer.Option("--list", help="Print the menu instead of speaking it.")
    ] = False,
    version: Annotated[
        bool,
        typer.Option(
            "--version", callback=_version_callback, is_eager=True, help="Show version and exit."
        ),
    ] = False,
) -> None:
    """Read Sisal's football odds for the day aloud.

    Up/down move through a list, right opens an item, left goes back, space says the details,
    Esc quits.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[RichHandler(console=Console(stderr=True), show_path=False, show_time=False)],
        force=True,
    )
    now = datetime.now() if day is None else day
    voice = None if show else speaker(rate)
    if voice is not None:
        voice.start()
    say = Announcer(voice)
    try:
        say(speech.WAIT)
        try:
            schedule = parse_schedule(pdf or fetch())
        except (FetchError, ParseError) as exc:
            log.error("%s", exc)
            say(speech.UNAVAILABLE, wait=True)
            raise typer.Exit(1) from exc

        menu = build_menu(schedule.matches, now)
        if not menu.children:
            log.info("No matches left on %s", f"{now:%d/%m}")
            say(speech.NO_MATCHES, wait=True)
            return

        summary = speech.today(len(menu.matches()))
        if show:
            title = f"{summary} Quote aggiornate al {schedule.updated:%d/%m %H:%M}"
            console.print(_tree(menu, Tree(title)))
            return
        navigator = Navigator(menu)
        say(f"{summary} {navigator.current.label}")
        listen(navigator, say)
    except KeyboardInterrupt:
        pass
    finally:
        if voice is not None:
            voice.close()
