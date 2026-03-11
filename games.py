#!/usr/bin/env python3
import curses
import random
import time


def _safe(win, row, col, text, attr=0):
    try:
        win.addstr(row, col, text, attr)
    except curses.error:
        pass


# ── HANGMAN ────────────────────────────────────────────────────────────────────

def run_hangman(stdscr):
    WORDS = [
        "python", "terminal", "keyboard", "monitor", "program",
        "function", "variable", "integer", "boolean", "library",
        "algorithm", "database", "network", "compiler", "debugger",
        "recursion", "iterator", "exception", "interface", "module",
        "penguin", "dolphin", "elephant", "cheetah", "crocodile",
        "volcano", "glacier", "tornado", "tsunami", "avalanche",
        "guitar", "trumpet", "violin", "saxophone", "keyboard",
        "chocolate", "avocado", "broccoli", "cinnamon", "blueberry",
        "adventure", "mystery", "fantasy", "thriller", "comedy",
        "architect", "engineer", "surgeon", "astronaut", "detective",
    ]

    STAGES = [
        ["  +---+", "  |   |", "      |", "      |", "      |", "      |", "========="],
        ["  +---+", "  |   |", "  O   |", "      |", "      |", "      |", "========="],
        ["  +---+", "  |   |", "  O   |", "  |   |", "      |", "      |", "========="],
        ["  +---+", "  |   |", "  O   |", " /|   |", "      |", "      |", "========="],
        ["  +---+", "  |   |", "  O   |", " /|\\  |", "      |", "      |", "========="],
        ["  +---+", "  |   |", "  O   |", " /|\\  |", " /    |", "      |", "========="],
        ["  +---+", "  |   |", "  O   |", " /|\\  |", " / \\  |", "      |", "========="],
    ]

    MAX_WRONG = len(STAGES) - 1

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED,   -1)
    curses.init_pair(2, curses.COLOR_WHITE, -1)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.curs_set(0)

    class Game:
        def __init__(self):
            self.word    = random.choice(WORDS)
            self.guessed = set()
            self.wrong   = []
            self.state   = "playing"
            self.message = "Guess a letter."

        @property
        def wrong_count(self):
            return len(self.wrong)

        @property
        def display_word(self):
            return " ".join(c if c in self.guessed else "_" for c in self.word)

        def guess(self, letter):
            if letter in self.guessed or letter in self.wrong:
                self.message = f"Already guessed '{letter}'."
                return
            self.guessed.add(letter)
            if letter in self.word:
                if all(c in self.guessed for c in self.word):
                    self.state   = "won"
                    self.message = f"You got it! The word was '{self.word}'."
                else:
                    self.message = f"Good — '{letter}' is in the word!"
            else:
                self.wrong.append(letter)
                if self.wrong_count >= MAX_WRONG:
                    self.state   = "lost"
                    self.message = f"Hanged! The word was '{self.word}'."
                else:
                    remaining = MAX_WRONG - self.wrong_count
                    self.message = f"'{letter}' is not in the word. {remaining} guess{'es' if remaining != 1 else ''} left."

    def draw(game):
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        oy = max(0, (h - 16) // 2)
        ox = max(0, (w - 50) // 2)

        stage = STAGES[min(game.wrong_count, MAX_WRONG)]
        gallows_attr = curses.color_pair(1) if game.state == "lost" else curses.color_pair(2)
        for i, line in enumerate(stage):
            _safe(stdscr, oy + i, ox, line, gallows_attr)

        wx = ox + 16
        _safe(stdscr, oy + 2, wx, "WORD", curses.A_BOLD)
        word_attr = curses.color_pair(1) if game.state == "lost" else (curses.color_pair(2) if game.state == "won" else 0)
        display = game.display_word if game.state != "lost" else " ".join(game.word)
        _safe(stdscr, oy + 3, wx, display, word_attr | curses.A_BOLD)

        _safe(stdscr, oy + 5, wx, "WRONG LETTERS", curses.A_BOLD)
        wrong_str = "  ".join(game.wrong) if game.wrong else "-"
        _safe(stdscr, oy + 6, wx, wrong_str, curses.color_pair(1) | curses.A_BOLD)

        _safe(stdscr, oy + 8, wx, f"Wrong: {game.wrong_count}/{MAX_WRONG}")
        _safe(stdscr, oy + 11, ox, game.message, curses.A_BOLD)

        if game.state == "playing":
            _safe(stdscr, oy + 13, ox, "Type a letter to guess    Q: quit    M: menu")
        else:
            _safe(stdscr, oy + 13, ox, "N: new game    Q: quit    M: menu")
        stdscr.refresh()

    game = Game()
    while True:
        draw(game)
        key = stdscr.getch()
        if key in (ord('q'), ord('Q')):
            return "quit"
        if key in (ord('m'), ord('M')):
            return "menu"
        if key in (ord('n'), ord('N')):
            game = Game()
            continue
        if game.state == "playing" and 97 <= key <= 122:
            game.guess(chr(key))
        elif game.state == "playing" and 65 <= key <= 90:
            game.guess(chr(key + 32))


# ── BLACKJACK ──────────────────────────────────────────────────────────────────

def run_blackjack(stdscr):
    SUITS = ["♠", "♥", "♦", "♣"]
    RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    RED_SUITS = {"♥", "♦"}
    STARTING_BALANCE = 1000

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED,   -1)
    curses.init_pair(2, curses.COLOR_WHITE, -1)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.curs_set(0)

    def card_value(rank):
        if rank in ("J", "Q", "K"):
            return 10
        if rank == "A":
            return 11
        return int(rank)

    def hand_total(hand):
        total = sum(card_value(r) for r, _ in hand)
        aces = sum(1 for r, _ in hand if r == "A")
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    def is_bust(hand):
        return hand_total(hand) > 21

    def is_blackjack(hand):
        return len(hand) == 2 and hand_total(hand) == 21

    def new_deck():
        deck = [(r, s) for s in SUITS for r in RANKS]
        random.shuffle(deck)
        return deck

    def deal(deck, n=1):
        cards = []
        for _ in range(n):
            if not deck:
                deck.extend(new_deck())
            cards.append(deck.pop())
        return cards

    def draw_card(row, col, rank, suit, face_down=False):
        if face_down:
            lines = ["┌─────┐", "│░░░░░│", "│░░░░░│", "│░░░░░│", "└─────┘"]
            for i, line in enumerate(lines):
                _safe(stdscr, row + i, col, line)
            return
        attr = curses.color_pair(1) if suit in RED_SUITS else curses.color_pair(2)
        rank_str = rank.ljust(2)
        lines = ["┌─────┐", f"│{rank_str}   │", f"│  {suit}  │", f"│   {rank_str}│", "└─────┘"]
        for i, line in enumerate(lines):
            _safe(stdscr, row + i, col, line, attr)

    def draw_hand(row, col, hand, label, hide_second=False):
        _safe(stdscr, row, col, label, curses.A_BOLD)
        for i, (rank, suit) in enumerate(hand):
            draw_card(row + 1, col + i * 8, rank, suit, hide_second and i == 1)
        total_row = row + 7
        if hide_second:
            _safe(stdscr, total_row, col, "Total: ?  ")
        else:
            total = hand_total(hand)
            label_str = f"Total: {total}"
            if total > 21:
                label_str += "  BUST"
            elif total == 21 and len(hand) == 2:
                label_str += "  BLACKJACK!"
            _safe(stdscr, total_row, col, label_str)

    class Game:
        def __init__(self):
            self.deck      = new_deck()
            self.balance   = STARTING_BALANCE
            self.bet       = 0
            self.player    = []
            self.dealer    = []
            self.state     = "betting"
            self.message   = ""
            self.bet_input = ""

        def place_bet(self, amount):
            if amount < 1 or amount > self.balance:
                self.message = f"Bet must be between 1 and {self.balance}."
                return
            self.bet = amount
            self.player = deal(self.deck, 2)
            self.dealer = deal(self.deck, 2)
            self.message = ""
            if is_blackjack(self.player):
                self.state = "dealer_turn"
                self._dealer_play()
            else:
                self.state = "player_turn"

        def hit(self):
            if self.state != "player_turn":
                return
            self.player += deal(self.deck)
            if is_bust(self.player):
                self.balance -= self.bet
                self.message = f"Bust! You lose ${self.bet}."
                self.state = "round_over"
            elif hand_total(self.player) == 21:
                self._stand()

        def stand(self):
            if self.state != "player_turn":
                return
            self._stand()

        def double_down(self):
            if self.state != "player_turn" or len(self.player) != 2:
                return
            if self.bet * 2 > self.balance:
                self.message = "Not enough balance to double down."
                return
            self.bet *= 2
            self.player += deal(self.deck)
            if is_bust(self.player):
                self.balance -= self.bet
                self.message = f"Bust! You lose ${self.bet}."
                self.state = "round_over"
            else:
                self._stand()

        def _stand(self):
            self.state = "dealer_turn"
            self._dealer_play()

        def _dealer_play(self):
            while hand_total(self.dealer) < 17:
                self.dealer += deal(self.deck)
            pt = hand_total(self.player)
            dt = hand_total(self.dealer)
            pbj = is_blackjack(self.player)
            dbj = is_blackjack(self.dealer)
            if pbj and dbj:
                self.message = "Both blackjack — push."
            elif pbj:
                w = int(self.bet * 1.5)
                self.balance += w
                self.message = f"Blackjack! You win ${w}!"
            elif dbj:
                self.balance -= self.bet
                self.message = f"Dealer blackjack. You lose ${self.bet}."
            elif is_bust(self.dealer):
                self.balance += self.bet
                self.message = f"Dealer busts! You win ${self.bet}!"
            elif pt > dt:
                self.balance += self.bet
                self.message = f"You win ${self.bet}!"
            elif dt > pt:
                self.balance -= self.bet
                self.message = f"Dealer wins. You lose ${self.bet}."
            else:
                self.message = "Push — it's a tie."
            self.state = "round_over"

        def new_round(self):
            if self.balance <= 0:
                self.balance = STARTING_BALANCE
                self.message = "Out of funds — balance reset to $1000."
            self.bet = 0
            self.player = []
            self.dealer = []
            self.bet_input = ""
            self.state = "betting"

    def draw(game):
        stdscr.erase()
        _, w = stdscr.getmaxyx()
        ox = max(2, (w - 60) // 2)
        oy = 1
        _safe(stdscr, oy, ox, "BLACKJACK", curses.A_BOLD)
        _safe(stdscr, oy, ox + 20, f"Balance: ${game.balance}", curses.A_BOLD)
        if game.state == "betting":
            _safe(stdscr, oy + 2, ox, f"Enter bet (1–{game.balance}) and press Enter:")
            _safe(stdscr, oy + 3, ox, f"  > ${game.bet_input}_")
            if game.message:
                _safe(stdscr, oy + 5, ox, game.message, curses.color_pair(1))
            _safe(stdscr, oy + 7, ox, "Q  Quit    M  Menu")
        else:
            hide = game.state == "player_turn"
            draw_hand(oy + 2,  ox, game.dealer, "Dealer", hide_second=hide)
            draw_hand(oy + 12, ox, game.player, "You")
            if game.message:
                _safe(stdscr, oy + 21, ox, game.message, curses.A_BOLD)
            if game.state == "player_turn":
                actions = "H  Hit    S  Stand"
                if len(game.player) == 2 and game.bet * 2 <= game.balance:
                    actions += "    D  Double down"
                _safe(stdscr, oy + 23, ox, actions)
            elif game.state == "round_over":
                _safe(stdscr, oy + 23, ox, "N  Next round    Q  Quit    M  Menu")
        stdscr.refresh()

    game = Game()
    while True:
        draw(game)
        key = stdscr.getch()
        if key in (ord('q'), ord('Q')):
            return "quit"
        if key in (ord('m'), ord('M')):
            return "menu"
        if game.state == "betting":
            if ord('0') <= key <= ord('9'):
                game.bet_input += chr(key)
                game.message = ""
            elif key in (curses.KEY_BACKSPACE, 127, 8):
                game.bet_input = game.bet_input[:-1]
            elif key in (ord('\n'), ord('\r'), curses.KEY_ENTER):
                if game.bet_input:
                    game.place_bet(int(game.bet_input))
        elif game.state == "player_turn":
            if key in (ord('h'), ord('H')):
                game.hit()
            elif key in (ord('s'), ord('S')):
                game.stand()
            elif key in (ord('d'), ord('D')):
                game.double_down()
        elif game.state == "round_over":
            if key in (ord('n'), ord('N')):
                game.new_round()


# ── BATTLESHIP ─────────────────────────────────────────────────────────────────

def run_battleship(stdscr):
    SHIPS = [
        ("Carrier",    5),
        ("Battleship", 4),
        ("Cruiser",    3),
        ("Submarine",  3),
        ("Destroyer",  2),
    ]

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED,   -1)
    curses.init_pair(2, curses.COLOR_WHITE, -1)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.curs_set(0)

    def can_place(board, r, c, size, horiz):
        for i in range(size):
            rr = r + (0 if horiz else i)
            cc = c + (i if horiz else 0)
            if not (0 <= rr < 10 and 0 <= cc < 10) or board[rr][cc]:
                return False
        return True

    def place_ships_random(board):
        for sid, (_, size) in enumerate(SHIPS, 1):
            placed = False
            while not placed:
                horiz = random.choice([True, False])
                r = random.randint(0, 9)
                c = random.randint(0, 9)
                if can_place(board, r, c, size, horiz):
                    for i in range(size):
                        rr = r + (0 if horiz else i)
                        cc = c + (i if horiz else 0)
                        board[rr][cc] = sid
                    placed = True

    class Game:
        def __init__(self):
            self.player_board = [[0]*10 for _ in range(10)]
            self.ai_board     = [[0]*10 for _ in range(10)]
            self.player_view  = [['·']*10 for _ in range(10)]
            self.ai_view      = [['·']*10 for _ in range(10)]
            self.cursor       = [0, 0]
            self.state        = "player_turn"
            self.message      = "Your turn — arrows to move, Enter to fire."
            self.winner       = None
            self.player_hp    = {sid: SHIPS[sid-1][1] for sid in range(1, 6)}
            self.ai_hp        = {sid: SHIPS[sid-1][1] for sid in range(1, 6)}
            self.ai_targets   = []
            place_ships_random(self.player_board)
            place_ships_random(self.ai_board)

        def all_sunk(self, hp):
            return all(v == 0 for v in hp.values())

        def player_fire(self):
            r, c = self.cursor
            if self.player_view[r][c] != '·':
                self.message = "Already fired there, pick another cell."
                return
            sid = self.ai_board[r][c]
            if sid:
                self.player_view[r][c] = 'X'
                self.ai_hp[sid] -= 1
                if self.ai_hp[sid] == 0:
                    self.message = f"You sunk the enemy {SHIPS[sid-1][0]}!"
                else:
                    self.message = "Hit!"
                if self.all_sunk(self.ai_hp):
                    self.state  = "game_over"
                    self.winner = "player"
                    self.message = "You sunk all enemy ships!  N: new game   Q: quit"
                    return
            else:
                self.player_view[r][c] = 'O'
                self.message = "Miss."
            self.state = "ai_turn"
            self.ai_fire()

        def ai_fire(self):
            self.ai_targets = [(r, c) for r, c in self.ai_targets if self.ai_view[r][c] == '·']
            if self.ai_targets:
                r, c = self.ai_targets.pop(random.randint(0, len(self.ai_targets) - 1))
            else:
                pool = [(r, c) for r in range(10) for c in range(10) if self.ai_view[r][c] == '·']
                if not pool:
                    self.state = "player_turn"
                    return
                r, c = random.choice(pool)
            sid = self.player_board[r][c]
            if sid:
                self.ai_view[r][c] = 'X'
                self.player_hp[sid] -= 1
                for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nr, nc = r+dr, c+dc
                    if 0 <= nr < 10 and 0 <= nc < 10 and self.ai_view[nr][nc] == '·' and (nr,nc) not in self.ai_targets:
                        self.ai_targets.append((nr, nc))
                if self.player_hp[sid] == 0:
                    self.message += f"  AI sunk your {SHIPS[sid-1][0]}!"
                    self.ai_targets = []
                else:
                    self.message += "  AI hit!"
                if self.all_sunk(self.player_hp):
                    self.state  = "game_over"
                    self.winner = "ai"
                    self.message = "AI sunk all your ships!  N: new game   Q: quit"
                    return
            else:
                self.ai_view[r][c] = 'O'
                self.message += "  AI missed."
            self.state = "player_turn"

    def draw(game):
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        oy = max(0, (h - 20) // 2)
        ox = max(0, (w - 78) // 2)
        col_header = "A B C D E F G H I J"

        _safe(stdscr, oy,     ox,      "YOUR BOARD",  curses.A_BOLD)
        _safe(stdscr, oy + 1, ox + 3,  col_header,    curses.color_pair(2))
        for r in range(10):
            _safe(stdscr, oy + 2 + r, ox, f"{r+1:2d}")
            for c in range(10):
                sid     = game.player_board[r][c]
                ai_shot = game.ai_view[r][c]
                if ai_shot == 'X':
                    cell, attr = 'X', curses.color_pair(1) | curses.A_BOLD
                elif ai_shot == 'O':
                    cell, attr = 'o', 0
                elif sid:
                    cell, attr = '#', curses.color_pair(2)
                else:
                    cell, attr = '·', 0
                _safe(stdscr, oy + 2 + r, ox + 3 + c * 2, cell, attr)

        ex = ox + 26
        _safe(stdscr, oy,     ex,      "ENEMY BOARD", curses.A_BOLD)
        _safe(stdscr, oy + 1, ex + 3,  col_header,    curses.color_pair(2))
        for r in range(10):
            _safe(stdscr, oy + 2 + r, ex, f"{r+1:2d}")
            for c in range(10):
                shot   = game.player_view[r][c]
                is_cur = (game.state == "player_turn" and game.cursor == [r, c])
                if shot == 'X':
                    cell, attr = 'X', curses.color_pair(1) | curses.A_BOLD
                elif shot == 'O':
                    cell, attr = 'o', 0
                else:
                    cell, attr = '·', 0
                if is_cur:
                    cell = '+' if shot == '·' else cell
                    attr = curses.color_pair(3)
                _safe(stdscr, oy + 2 + r, ex + 3 + c * 2, cell, attr)

        sx = ox + 54
        _safe(stdscr, oy, sx, "YOUR FLEET", curses.A_BOLD)
        for i, (name, size) in enumerate(SHIPS):
            sid  = i + 1
            hp   = game.player_hp[sid]
            bar  = '#' * hp + '·' * (size - hp)
            attr = curses.color_pair(1) if hp == 0 else curses.color_pair(2)
            _safe(stdscr, oy + 1 + i, sx, f"{name:<12}{bar}", attr)

        _safe(stdscr, oy + 7, sx, "ENEMY FLEET", curses.A_BOLD)
        for i, (name, size) in enumerate(SHIPS):
            sid  = i + 1
            hp   = game.ai_hp[sid]
            if hp == 0:
                bar, attr = "SUNK", curses.color_pair(1)
            else:
                bar, attr = '?' * size, 0
            _safe(stdscr, oy + 8 + i, sx, f"{name:<12}{bar}", attr)

        _safe(stdscr, oy + 14, ox, game.message, curses.A_BOLD)
        _safe(stdscr, oy + 16, ox, "Arrows: move    Space: fire    N: new game    Q: quit    M: menu")
        stdscr.refresh()

    game = Game()
    while True:
        draw(game)
        key = stdscr.getch()
        if key in (ord('q'), ord('Q')):
            return "quit"
        if key in (ord('m'), ord('M')):
            return "menu"
        if key in (ord('n'), ord('N')):
            game = Game()
            continue
        if game.state == "player_turn":
            r, c = game.cursor
            if key == curses.KEY_UP:
                game.cursor[0] = max(0, r - 1)
            elif key == curses.KEY_DOWN:
                game.cursor[0] = min(9, r + 1)
            elif key == curses.KEY_LEFT:
                game.cursor[1] = max(0, c - 1)
            elif key == curses.KEY_RIGHT:
                game.cursor[1] = min(9, c + 1)
            elif key in (ord(' '),):
                game.player_fire()


# ── 2048 ───────────────────────────────────────────────────────────────────────

def run_2048(stdscr):
    SIZE   = 4
    CELL_W = 6
    CELL_H = 3

    TILE_PAIRS = {
        2: 1, 4: 2, 8: 3, 16: 4, 32: 5, 64: 6,
        128: 7, 256: 8, 512: 9, 1024: 10, 2048: 11,
    }

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1,  curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2,  curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(3,  curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(4,  curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(5,  curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(6,  curses.COLOR_WHITE, curses.COLOR_MAGENTA)
    curses.init_pair(7,  curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(8,  curses.COLOR_BLACK, curses.COLOR_YELLOW)
    curses.init_pair(9,  curses.COLOR_BLACK, curses.COLOR_GREEN)
    curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(11, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(12, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.curs_set(0)

    def tile_attr(val):
        pair = TILE_PAIRS.get(val, 11)
        bold = curses.A_BOLD if val >= 256 else 0
        return curses.color_pair(pair) | bold

    class Game:
        def __init__(self):
            self.board = [[0] * SIZE for _ in range(SIZE)]
            self.score = 0
            self.best  = 0
            self.over  = False
            self.won   = False
            self.keep_playing = False
            self._spawn()
            self._spawn()

        def _empties(self):
            return [(r, c) for r in range(SIZE) for c in range(SIZE) if self.board[r][c] == 0]

        def _spawn(self):
            cells = self._empties()
            if cells:
                r, c = random.choice(cells)
                self.board[r][c] = 4 if random.random() < 0.1 else 2

        def _slide(self, row):
            tiles = [x for x in row if x]
            result, score, i = [], 0, 0
            while i < len(tiles):
                if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
                    v = tiles[i] * 2
                    result.append(v)
                    score += v
                    i += 2
                else:
                    result.append(tiles[i])
                    i += 1
            result += [0] * (SIZE - len(result))
            return result, score

        def move(self, direction):
            if self.over or (self.won and not self.keep_playing):
                return
            prev  = [row[:] for row in self.board]
            total = 0
            if direction == 'left':
                for r in range(SIZE):
                    self.board[r], s = self._slide(self.board[r])
                    total += s
            elif direction == 'right':
                for r in range(SIZE):
                    new, s = self._slide(self.board[r][::-1])
                    self.board[r] = new[::-1]
                    total += s
            elif direction == 'up':
                for c in range(SIZE):
                    col = [self.board[r][c] for r in range(SIZE)]
                    new, s = self._slide(col)
                    for r in range(SIZE):
                        self.board[r][c] = new[r]
                    total += s
            elif direction == 'down':
                for c in range(SIZE):
                    col = [self.board[r][c] for r in range(SIZE)][::-1]
                    new, s = self._slide(col)
                    new = new[::-1]
                    for r in range(SIZE):
                        self.board[r][c] = new[r]
                    total += s
            changed = any(self.board[r][c] != prev[r][c] for r in range(SIZE) for c in range(SIZE))
            if changed:
                self.score += total
                if self.score > self.best:
                    self.best = self.score
                self._spawn()
                if not self.won and any(2048 in row for row in self.board):
                    self.won = True
                if not self._can_move():
                    self.over = True

        def _can_move(self):
            if self._empties():
                return True
            for r in range(SIZE):
                for c in range(SIZE):
                    v = self.board[r][c]
                    if c + 1 < SIZE and self.board[r][c + 1] == v:
                        return True
                    if r + 1 < SIZE and self.board[r + 1][c] == v:
                        return True
            return False

    def draw_overlay(h, w, lines):
        mw = max(len(l) for l in lines)
        mr = max(0, h // 2 - len(lines) // 2)
        mc = max(0, (w - mw) // 2)
        attr = curses.color_pair(12) | curses.A_BOLD
        for i, line in enumerate(lines):
            _safe(stdscr, mr + i, mc, line.ljust(mw), attr)

    def draw(game):
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        grid_w = 1 + SIZE * (CELL_W + 1)
        grid_h = 1 + SIZE * (CELL_H + 1)
        ox = max(0, (w - grid_w) // 2)
        oy = max(0, (h - grid_h - 3) // 2)

        _safe(stdscr, oy, ox, "2048", curses.A_BOLD)
        _safe(stdscr, oy + 1, ox, f"Score: {game.score:<10}  Best: {game.best}")
        oy += 3

        top = "┌" + ("─" * CELL_W + "┬") * (SIZE - 1) + "─" * CELL_W + "┐"
        mid = "├" + ("─" * CELL_W + "┼") * (SIZE - 1) + "─" * CELL_W + "┤"
        bot = "└" + ("─" * CELL_W + "┴") * (SIZE - 1) + "─" * CELL_W + "┘"

        for gr in range(SIZE):
            _safe(stdscr, oy + gr * (CELL_H + 1), ox, top if gr == 0 else mid)
        _safe(stdscr, oy + SIZE * (CELL_H + 1), ox, bot)

        for gr in range(SIZE):
            for ro in range(CELL_H):
                sr = oy + gr * (CELL_H + 1) + 1 + ro
                _safe(stdscr, sr, ox, "│" + ("│".join(" " * CELL_W for _ in range(SIZE))) + "│")

        for gr in range(SIZE):
            for gc in range(SIZE):
                val = game.board[gr][gc]
                if val == 0:
                    continue
                attr     = tile_attr(val)
                sr_top   = oy + gr * (CELL_H + 1) + 1
                sc_left  = ox + 1 + gc * (CELL_W + 1)
                for ro in range(CELL_H):
                    text = str(val).center(CELL_W) if ro == CELL_H // 2 else " " * CELL_W
                    _safe(stdscr, sr_top + ro, sc_left, text, attr)

        _safe(stdscr, oy + grid_h + 1, ox, "←/→/↑/↓  Move    N  New game    Q  Quit    M  Menu")

        if game.won and not game.keep_playing:
            draw_overlay(h, w, [
                "                ",
                "   YOU WIN!     ",
                "                ",
                "   C: Continue  ",
                "   N: New game  ",
                "                ",
            ])
        if game.over:
            draw_overlay(h, w, [
                "                    ",
                "   GAME OVER        ",
                f"   Score: {game.score:<8}   ",
                "                    ",
                "   N: New game      ",
                "   Q: Quit          ",
                "                    ",
            ])
        stdscr.refresh()

    game = Game()
    while True:
        draw(game)
        key = stdscr.getch()
        if key in (ord('q'), ord('Q')):
            return "quit"
        if key in (ord('m'), ord('M')):
            return "menu"
        elif key in (ord('n'), ord('N')):
            game = Game()
        elif key in (ord('c'), ord('C')):
            game.keep_playing = True
        elif key == curses.KEY_LEFT:
            game.move('left')
        elif key == curses.KEY_RIGHT:
            game.move('right')
        elif key == curses.KEY_UP:
            game.move('up')
        elif key == curses.KEY_DOWN:
            game.move('down')


# ── TETRIS ─────────────────────────────────────────────────────────────────────

def run_tetris(stdscr):
    BOARD_W = 10
    BOARD_H = 20

    PIECES = [
        [[(0, 0), (0, 1), (0, 2), (0, 3)], [(0, 0), (1, 0), (2, 0), (3, 0)]],
        [[(0, 0), (0, 1), (1, 0), (1, 1)]],
        [[(0, 1), (1, 0), (1, 1), (1, 2)], [(0, 0), (1, 0), (1, 1), (2, 0)],
         [(0, 0), (0, 1), (0, 2), (1, 1)], [(0, 1), (1, 0), (1, 1), (2, 1)]],
        [[(0, 1), (0, 2), (1, 0), (1, 1)], [(0, 0), (1, 0), (1, 1), (2, 1)]],
        [[(0, 0), (0, 1), (1, 1), (1, 2)], [(0, 1), (1, 0), (1, 1), (2, 0)]],
        [[(0, 0), (1, 0), (1, 1), (1, 2)], [(0, 0), (0, 1), (1, 0), (2, 0)],
         [(0, 0), (0, 1), (0, 2), (1, 2)], [(0, 1), (1, 1), (2, 0), (2, 1)]],
        [[(0, 2), (1, 0), (1, 1), (1, 2)], [(0, 0), (1, 0), (2, 0), (2, 1)],
         [(0, 0), (0, 1), (0, 2), (1, 0)], [(0, 0), (0, 1), (1, 1), (2, 1)]],
    ]

    PIECE_COLORS = [1, 2, 3, 4, 5, 6, 7]
    LINE_SCORES  = [0, 100, 300, 500, 800]

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN,    -1)
    curses.init_pair(2, curses.COLOR_YELLOW,  -1)
    curses.init_pair(3, curses.COLOR_MAGENTA, -1)
    curses.init_pair(4, curses.COLOR_GREEN,   -1)
    curses.init_pair(5, curses.COLOR_RED,     -1)
    curses.init_pair(6, curses.COLOR_BLUE,    -1)
    curses.init_pair(7, curses.COLOR_WHITE,   -1)
    curses.init_pair(8, curses.COLOR_WHITE,   -1)
    curses.init_pair(9, curses.COLOR_BLACK,   curses.COLOR_WHITE)
    curses.curs_set(0)

    stdscr.nodelay(True)
    stdscr.timeout(33)

    def fall_speed(level):
        return max(0.05, 0.8 - (level - 1) * 0.07)

    class Game:
        def __init__(self):
            self.board = [[0] * BOARD_W for _ in range(BOARD_H)]
            self.score = 0
            self.level = 1
            self.lines = 0
            self.paused = False
            self.over   = False
            self._bag: list = []
            self.next_idx  = self._draw()
            self.hold_idx  = None
            self.can_hold  = True
            self._spawn()
            self.last_fall = time.time()

        def _draw(self):
            if not self._bag:
                self._bag = list(range(7))
                random.shuffle(self._bag)
            return self._bag.pop()

        def _spawn(self):
            self.cur_idx  = self.next_idx
            self.next_idx = self._draw()
            self.rot  = 0
            self.row  = 0
            self.col  = 3
            self.can_hold = True
            if not self._ok(self.row, self.col, self.rot):
                self.over = True

        def _cells(self, row, col, idx, rot):
            rots = PIECES[idx]
            return [(row + dr, col + dc) for dr, dc in rots[rot % len(rots)]]

        def _ok(self, row, col, rot):
            for r, c in self._cells(row, col, self.cur_idx, rot):
                if not (0 <= r < BOARD_H and 0 <= c < BOARD_W):
                    return False
                if self.board[r][c]:
                    return False
            return True

        def _lock(self):
            color = self.cur_idx + 1
            for r, c in self._cells(self.row, self.col, self.cur_idx, self.rot):
                if 0 <= r < BOARD_H:
                    self.board[r][c] = color
            self._clear_lines()
            self._spawn()

        def _clear_lines(self):
            kept = [row for row in self.board if not all(row)]
            n = BOARD_H - len(kept)
            if n:
                self.board  = [[0] * BOARD_W for _ in range(n)] + kept
                self.lines += n
                self.score += LINE_SCORES[n] * self.level
                self.level  = self.lines // 10 + 1

        def ghost_row(self):
            r = self.row
            while self._ok(r + 1, self.col, self.rot):
                r += 1
            return r

        def move(self, dc):
            if self._ok(self.row, self.col + dc, self.rot):
                self.col += dc

        def rotate(self, d=1):
            rots = PIECES[self.cur_idx]
            new_rot = (self.rot + d) % len(rots)
            for dc in [0, 1, -1, 2, -2]:
                if self._ok(self.row, self.col + dc, new_rot):
                    self.col += dc
                    self.rot  = new_rot
                    return

        def soft_drop(self):
            if self._ok(self.row + 1, self.col, self.rot):
                self.row  += 1
                self.score += 1
            else:
                self._lock()
            self.last_fall = time.time()

        def hard_drop(self):
            g = self.ghost_row()
            self.score += 2 * (g - self.row)
            self.row = g
            self._lock()
            self.last_fall = time.time()

        def hold(self):
            if not self.can_hold:
                return
            if self.hold_idx is None:
                self.hold_idx = self.cur_idx
                self._spawn()
            else:
                self.cur_idx, self.hold_idx = self.hold_idx, self.cur_idx
                self.rot = 0
                self.row = 0
                self.col = 3
            self.can_hold = False

        def tick(self):
            if self.paused or self.over:
                return
            now = time.time()
            if now - self.last_fall >= fall_speed(self.level):
                if self._ok(self.row + 1, self.col, self.rot):
                    self.row += 1
                else:
                    self._lock()
                self.last_fall = now

    def draw_preview(top, left, piece_idx):
        color = curses.color_pair(PIECE_COLORS[piece_idx])
        for dr, dc in PIECES[piece_idx][0]:
            _safe(stdscr, top + dr, left + dc * 2, "██", color)

    def draw(game):
        stdscr.erase()
        h, w = stdscr.getmaxyx()
        total_w = 12 + BOARD_W * 2 + 2 + 2 + 16
        total_h = BOARD_H + 2
        ox = max(0, (w - total_w) // 2)
        oy = max(0, (h - total_h) // 2)

        hold_x  = ox
        board_x = ox + 12
        info_x  = board_x + BOARD_W * 2 + 2 + 2

        ghost_r     = game.ghost_row()
        ghost_cells = set(game._cells(ghost_r, game.col, game.cur_idx, game.rot))
        cur_cells   = set(game._cells(game.row, game.col, game.cur_idx, game.rot))

        _safe(stdscr, oy, board_x, "╔" + "══" * BOARD_W + "╗")
        _safe(stdscr, oy + BOARD_H + 1, board_x, "╚" + "══" * BOARD_W + "╝")
        for r in range(BOARD_H):
            _safe(stdscr, oy + 1 + r, board_x, "║")
            _safe(stdscr, oy + 1 + r, board_x + BOARD_W * 2 + 1, "║")

        for r in range(BOARD_H):
            for c in range(BOARD_W):
                sr = oy + 1 + r
                sc = board_x + 1 + c * 2
                if (r, c) in cur_cells:
                    _safe(stdscr, sr, sc, "██", curses.color_pair(PIECE_COLORS[game.cur_idx]))
                elif (r, c) in ghost_cells:
                    _safe(stdscr, sr, sc, "░░", curses.color_pair(8) | curses.A_DIM)
                elif game.board[r][c]:
                    _safe(stdscr, sr, sc, "██", curses.color_pair(game.board[r][c]))

        _safe(stdscr, oy,     info_x, "┌──────────┐")
        _safe(stdscr, oy + 1, info_x, "│  TETRIS  │", curses.A_BOLD)
        _safe(stdscr, oy + 2, info_x, "└──────────┘")
        _safe(stdscr, oy + 4, info_x, "Score")
        _safe(stdscr, oy + 5, info_x, f"{game.score:>10,}", curses.A_BOLD)
        _safe(stdscr, oy + 7, info_x, f"Level   {game.level:>3}")
        _safe(stdscr, oy + 8, info_x, f"Lines   {game.lines:>3}")
        _safe(stdscr, oy + 10, info_x, "NEXT:")
        draw_preview(oy + 11, info_x, game.next_idx)

        controls = [
            ("←/→", "Move"), ("↑/Z", "Rotate"), ("↓  ", "Soft drop"),
            ("SPC", "Hard drop"), ("C  ", "Hold"), ("P  ", "Pause"),
            ("Q  ", "Quit"), ("M  ", "Menu"),
        ]
        _safe(stdscr, oy + 16, info_x, "Controls:")
        for i, (key, action) in enumerate(controls):
            _safe(stdscr, oy + 17 + i, info_x, f"{key}  {action}")

        _safe(stdscr, oy, hold_x, "HOLD:")
        if game.hold_idx is not None:
            attr = curses.color_pair(PIECE_COLORS[game.hold_idx])
            if not game.can_hold:
                attr |= curses.A_DIM
            for dr, dc in PIECES[game.hold_idx][0]:
                _safe(stdscr, oy + 1 + dr, hold_x + dc * 2, "██", attr)

        if game.paused:
            msg = "  PAUSED — press P to resume  "
            _safe(stdscr, h // 2, max(0, (w - len(msg)) // 2), msg, curses.color_pair(9) | curses.A_BOLD)

        if game.over:
            lines = [
                "            ", " GAME  OVER ", "            ",
                f" {game.score:>10,} ", "            ",
                " R: restart ", " Q: quit    ", " M: menu    ", "            ",
            ]
            mw = max(len(l) for l in lines)
            mr = max(0, h // 2 - len(lines) // 2)
            mc = max(0, (w - mw) // 2)
            for i, line in enumerate(lines):
                _safe(stdscr, mr + i, mc, line.ljust(mw), curses.color_pair(9) | curses.A_BOLD)

        stdscr.refresh()

    game = Game()
    result = "menu"
    try:
        while True:
            game.tick()
            draw(game)
            key = stdscr.getch()

            if key in (ord("q"), ord("Q")):
                result = "quit"
                break
            if key in (ord("m"), ord("M")):
                result = "menu"
                break

            if game.over:
                if key in (ord("r"), ord("R")):
                    game = Game()
                continue

            if key in (ord("p"), ord("P")):
                game.paused = not game.paused
            if game.paused:
                continue

            if key == curses.KEY_LEFT:
                game.move(-1)
            elif key == curses.KEY_RIGHT:
                game.move(1)
            elif key == curses.KEY_UP:
                game.rotate(1)
            elif key in (ord("z"), ord("Z")):
                game.rotate(-1)
            elif key == curses.KEY_DOWN:
                game.soft_drop()
            elif key == ord(" "):
                game.hard_drop()
            elif key in (ord("c"), ord("C")):
                game.hold()
    finally:
        stdscr.nodelay(False)
        stdscr.timeout(-1)

    return result


# ── MENU ───────────────────────────────────────────────────────────────────────

MENU_ITEMS = [
    ("Hangman",    run_hangman),
    ("Blackjack",  run_blackjack),
    ("Battleship", run_battleship),
    ("2048",       run_2048),
    ("Tetris",     run_tetris),
]


def draw_menu(stdscr, sel):
    stdscr.erase()
    h, w = stdscr.getmaxyx()

    title_lines = [
        " █████╗ ██████╗  ██████╗ █████╗ ██████╗ ███████╗",
        "██╔══██╗██╔══██╗██╔════╝██╔══██╗██╔══██╗██╔════╝",
        "███████║██████╔╝██║     ███████║██║  ██║█████╗  ",
        "██╔══██║██╔══██╗██║     ██╔══██║██║  ██║██╔══╝  ",
        "██║  ██║██║  ██║╚██████╗██║  ██║██████╔╝███████╗",
        "╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═════╝ ╚══════╝",
    ]

    title_w = max(len(l) for l in title_lines)
    ty = max(1, (h - len(title_lines) - len(MENU_ITEMS) - 6) // 2)
    tx = max(0, (w - title_w) // 2)

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN,  -1)
    curses.init_pair(2, curses.COLOR_WHITE, -1)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    for i, line in enumerate(title_lines):
        _safe(stdscr, ty + i, tx, line, curses.color_pair(1) | curses.A_BOLD)

    my = ty + len(title_lines) + 2
    for i, (name, _) in enumerate(MENU_ITEMS):
        label = f"  {name}  "
        mx = max(0, (w - len(label)) // 2)
        if i == sel:
            _safe(stdscr, my + i * 2, mx, label, curses.color_pair(3) | curses.A_BOLD)
        else:
            _safe(stdscr, my + i * 2, mx, label, curses.color_pair(2))

    hint = "↑/↓  Navigate    Enter  Select    Q  Quit"
    _safe(stdscr, h - 2, max(0, (w - len(hint)) // 2), hint)
    stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)
    sel = 0

    while True:
        draw_menu(stdscr, sel)
        key = stdscr.getch()

        if key in (ord('q'), ord('Q')):
            break
        elif key == curses.KEY_UP:
            sel = (sel - 1) % len(MENU_ITEMS)
        elif key == curses.KEY_DOWN:
            sel = (sel + 1) % len(MENU_ITEMS)
        elif key in (ord('\n'), ord('\r'), curses.KEY_ENTER):
            result = MENU_ITEMS[sel][1](stdscr)
            if result == "quit":
                break
            # result == "menu" → loop back to menu


curses.wrapper(main)
