# Terminal Arcade

A collection of five classic games running in one terminal app, built with Python and `curses`. No dependencies — just Python 3.

```
 █████╗ ██████╗  ██████╗ █████╗ ██████╗ ███████╗
██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔════╝
███████║██████╔╝██║     ███████║██║  ██║█████╗
██╔══██║██╔══██╗██║     ██╔══██║██║  ██║██╔══╝
██║  ██║██║  ██║╚██████╗██║  ██║██████╔╝███████╗
╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═════╝ ╚══════╝
```

## Games

| # | Game | Description |
|---|------|-------------|
| 1 | **Hangman** | Guess the hidden word letter by letter before the man is hanged |
| 2 | **Blackjack** | Classic casino card game — hit, stand, or double down |
| 3 | **Battleship** | Sink the AI's fleet before it sinks yours |
| 4 | **2048** | Slide tiles and merge them to reach the 2048 tile |
| 5 | **Tetris** | The timeless block-stacking game with hold, ghost piece, and levels |

## Requirements

- Python 3.8+
- A terminal with at least 80×24 characters (larger is better)
- `curses` — included in the Python standard library on macOS and Linux

> **Windows:** `curses` is not included by default. Install [`windows-curses`](https://pypi.org/project/windows-curses/) first:
> ```
> pip install windows-curses
> ```

## Running

```bash
python3 games.py
```

Navigate the menu with `↑` / `↓`, press `Enter` to launch a game.
Press `M` at any point to return to the menu, or `Q` to quit entirely.

---

## Controls

### Hangman
| Key | Action |
|-----|--------|
| `A`–`Z` | Guess a letter |
| `N` | New game |
| `M` | Back to menu |
| `Q` | Quit |

### Blackjack
| Key | Action |
|-----|--------|
| `0`–`9` + `Enter` | Enter your bet |
| `H` | Hit |
| `S` | Stand |
| `D` | Double down |
| `N` | New round |
| `M` | Back to menu |
| `Q` | Quit |

### Battleship
| Key | Action |
|-----|--------|
| `↑` `↓` `←` `→` | Move cursor |
| `Space` | Fire |
| `N` | New game |
| `M` | Back to menu |
| `Q` | Quit |

### 2048
| Key | Action |
|-----|--------|
| `↑` `↓` `←` `→` | Slide tiles |
| `C` | Continue after winning |
| `N` | New game |
| `M` | Back to menu |
| `Q` | Quit |

### Tetris
| Key | Action |
|-----|--------|
| `←` `→` | Move piece |
| `↑` | Rotate clockwise |
| `Z` | Rotate counter-clockwise |
| `↓` | Soft drop |
| `Space` | Hard drop |
| `C` | Hold piece |
| `P` | Pause / resume |
| `R` | Restart (after game over) |
| `M` | Back to menu |
| `Q` | Quit |

---

## Project Structure

```
games.py   — entire arcade in a single file (~500 lines)
```

Each game lives in its own `run_*()` function, so they're easy to read, modify, or extract independently.

## License

MIT
