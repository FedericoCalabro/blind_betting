# blind_betting

Reads the day's football odds from [Sisal](https://www.sisal.it) aloud, in Italian, and lets you
browse them with nothing but the arrow keys and the space bar.

> **Backstory:** my dad is almost blind. He has always enjoyed a bet on the football, but he can no
> longer read the odds. The first version (February 2023) was a handful of scripts that turned
> Sisal's daily PDF into a menu he could listen to. This is a complete rewrite as a proper, tested
> Python package, with simpler menus, more markets and a Windows exe built by GitHub Actions.

## How Dad uses it

Double-click `blind-betting.exe`. It says "Un momento.", downloads today's schedule, and then
"18 partite oggi. Prossime partite". From there:

| Key       | Does                                                       |
| --------- | ---------------------------------------------------------- |
| ↑ / ↓     | Previous / next item in the list (it wraps around)         |
| →         | Opens the item (on a match: its other markets)             |
| ←         | Goes back                                                  |
| Space     | Says the details: the odds of a match, or how many matches |
| Esc       | Quits (or just close the window)                           |

Only today's matches that haven't kicked off yet are listed:

```text
Prossime partite              the next 10 kick-offs
│  "18 e 30, Inter - Parma"
Favorite
├─ fino a 1 e 30              matches whose 1 or 2 is in the band, cheapest first (max 10)
├─ da 1 e 30 a 1 e 60         "Inter - Parma, uno 1 e 13"
└─ da 1 e 60 a 2
Goal
├─ Tanti goal                 cheapest over 2.5 first: "Inter - Parma, over 1 e 33"
└─ Pochi goal                 cheapest under 2.5 first
Campionati
└─ Italia › Serie A › "18 e 30, Inter - Parma"
```

Space on a match says `Serie A, ore 18 e 30. Uno 1 e 13, pareggio 8, due 20.` Right arrow on a
match opens four more markets, each read with space:

| Market        | Example                                                                     |
| ------------- | --------------------------------------------------------------------------- |
| Doppia chance | `Uno ics 1 e 17, ics due 1 e 90, uno due 1 e 33.`                           |
| Under over    | `Underino 2 e 60, overino 1 e 42. Under 1 e 57, over 2 e 25.`               |
| Goal no goal  | `Goal 2, no goal 1 e 72.`                                                   |
| Segna goal    | `Kazakistan sì 1 e 19, no 3 e 80. Moldova sì 1 e 60, no 2 e 10.`            |

Underino and overino are the 1.5 line, under and over the 2.5 one. Odds are spoken as "1 e 13",
not "1,13": every voice reads that the same way. Every sentence is
also printed in the console window, for whoever is sitting next to him.

## Install

### Windows (the exe)

1. Download `blind-betting.exe` from the
   [latest release](https://github.com/FedericoCalabro/blind_betting/releases/latest).
2. Make sure Windows has an Italian voice: *Settings → Time & language → Speech → Add voices →
   Italiano*. Without one, the default voice reads the Italian text.
3. Double-click the exe. Put a shortcut on the desktop, or give it a keyboard shortcut in the
   shortcut's properties, so it's easy to start without looking.

The keys are read globally, so they work even if the console window loses focus.

### Anywhere else (uv)

You only need [uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
uv tool install git+https://github.com/FedericoCalabro/blind_betting
blind-betting
```

On a Mac the voice is the system's `say` (Alice, if installed). The terminal needs
*System Settings → Privacy & Security → Accessibility* permission to read the arrow keys.

## Usage

```text
blind-betting [OPTIONS]
```

| Option           | Description                                                          |
| ---------------- | -------------------------------------------------------------------- |
| `--list`         | Print the menu as a tree instead of speaking it                      |
| `--pdf FILE`     | Read this PDF instead of downloading today's                         |
| `--date DAY`     | Show this whole day (`YYYY-MM-DD`), not just what's left of today    |
| `--rate N`       | Speech speed in words a minute (default 125)                         |
| `--version`      | Show the version and exit                                            |

`blind-betting --list` is the quickest way to check what Dad will hear today.

Which countries and leagues are included lives in
[`leagues.py`](src/blind_betting/leagues.py). Youth, women's and club-friendly competitions and the
lower divisions are left out. The size of the lists and the odds bands are at the top of
[`menu.py`](src/blind_betting/menu.py).

## How it works

1. **Download.** Sisal publishes the day's schedule as a PDF, *calcio base per manifestazione*.
   Its server drops connections whose TLS fingerprint isn't a real browser's, so it's fetched
   with [curl_cffi](https://github.com/lexiforest/curl_cffi) impersonating Chrome. The copy is
   kept in the user cache folder, and if a later download fails, that day's copy is used.
2. **Parse.** Every row of the PDF has 22 odds columns, and text extraction glues them together
   (`2,151,573,901,18`). So the parser reads word positions with
   [pdfplumber](https://github.com/jsvine/pdfplumber) instead. It finds the header row on each
   page and places every number in the column it sits under. Two-digit odds overflow into the next
   cell (`12,0022,00`), so each number is placed by its own characters. Handicap odds are dropped.
3. **Menu.** Today's remaining matches are filtered and grouped into the lists above.
4. **Speech and keys.** [pynput](https://github.com/moses-palmer/pynput) listens for the keys.
   Every key press interrupts the current sentence. On Windows the voice is SAPI5 through
   [pyttsx3](https://github.com/nateshmbhat/pyttsx3); on a Mac it's `say`.

## Building the Windows exe from a Mac

PyInstaller can't cross-compile, so the
[Windows workflow](.github/workflows/windows.yml) builds the exe on a GitHub Windows runner. It
lints, runs the tests and builds `blind-betting.exe`, then smoke-tests the exe against the fixture
PDF. It runs on every push to `main`, and the exe is attached to the run as an artifact. To publish
a release:

```bash
git tag v2.0.0
git push origin v2.0.0   # the workflow attaches blind-betting.exe to the v2.0.0 release
```

You can also start it by hand from the repo's *Actions* tab (*Run workflow*), or with the
[GitHub CLI](https://cli.github.com): `gh workflow run windows.yml`, then
`gh run download -n blind-betting`.

## Development

```bash
uv sync                    # runtime + dev dependencies into .venv
uv run blind-betting       # run from the checkout
uv run pytest              # offline test suite
uv run ruff check .        # lint
uv run ruff format .       # format
```

```text
src/blind_betting/
├── cli.py         # Typer command: download, parse, build the menu, speak, listen
├── sisal.py       # downloads the PDF (curl_cffi), falls back to today's cached copy
├── parser.py      # positional PDF parser → Match objects
├── leagues.py     # which countries and leagues are included
├── menu.py        # the menu tree
├── navigator.py   # what each key says, and the pynput listener
├── speech.py      # every Italian sentence
└── voice.py       # text to speech: SAPI5 (pyttsx3) on Windows, `say` on macOS
tests/
├── fixtures/palinsesto.pdf   # two pages of the real schedule of 2 October 2026
└── test_*.py
```

If Sisal changes the PDF layout, the parser stops with a clear error, and Dad hears
"Palinsesto non disponibile". Run `blind-betting --list` to see the error, save a fresh PDF
over the fixture, and let the failing tests point at what moved.

## Disclaimer

An unofficial, personal project, not affiliated with or endorsed by Sisal. Odds change during
the day: check them on the betting slip before you bet. Gioca responsabilmente.
