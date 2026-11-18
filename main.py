"""
CodeAlpha Python Programming Internship - Task 1: Hangman Game (Pro Edition)
----------------------------------------------------------------------------
A complete, production-grade console word-guessing game featuring:
- Full Object-Oriented Architecture (OOP) with Dataclasses & Enums
- Multi-tier difficulty system (Easy: 8 lives, Medium: 6 lives, Hard: 4 lives)
- Categorized word banks with contextual hints (includes CodeAlpha core words)
- Real-time ASCII gallows dashboard with live health meter & alphabet tracker
- Persistent disk-based stats & high-scores (stats.json)
- CLI argument support (--difficulty, --category, --stats, --reset-stats, --no-clear)
- Defensive input handling and graceful exit handling (Ctrl+C, EOF)
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field
from enum import Enum
import json
import os
from pathlib import Path
import random
import string
import sys
from typing import Optional

# Ensure UTF-8 output encoding across all operating systems
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ==============================================================================
# 1. CONSTANTS & ENUMS
# ==============================================================================

LINE_WIDTH = 76
STATS_FILE = Path("stats.json")

# The 5 original core words required for CodeAlpha Task 1
CORE_WORDS = ["python", "hangman", "developer", "keyboard", "programming"]


class Difficulty(Enum):
    """Game difficulty settings defining mistakes allowed and hint allowances."""
    EASY = ("Easy", 8, 2)
    MEDIUM = ("Medium", 6, 1)
    HARD = ("Hard", 4, 0)

    def __init__(self, display_name: str, max_mistakes: int, hints_allowed: int) -> None:
        self.display_name = display_name
        self.max_mistakes = max_mistakes
        self.hints_allowed = hints_allowed


class GuessResult(Enum):
    """Outcome of a player's guess attempt."""
    CORRECT = "CORRECT"
    WRONG = "WRONG"
    ALREADY_TRIED = "ALREADY_TRIED"
    INVALID = "INVALID"
    SOLVED_WORD = "SOLVED_WORD"
    WRONG_WORD = "WRONG_WORD"
    HINT_REVEALED = "HINT_REVEALED"
    HINT_EXHAUSTED = "HINT_EXHAUSTED"


# ==============================================================================
# 2. ASCII ART & VISUAL ASSETS
# ==============================================================================

# 7 Visual gallows stages (0 to 6 mistakes)
HANGMAN_STAGES_6 = [
    [
        "   +---+    ",
        "   |   |    ",
        "       |    ",
        "       |    ",
        "       |    ",
        "       |    ",
        "=========",
    ],
    [
        "   +---+    ",
        "   |   |    ",
        "   O   |    ",
        "       |    ",
        "       |    ",
        "       |    ",
        "=========",
    ],
    [
        "   +---+    ",
        "   |   |    ",
        "   O   |    ",
        "   |   |    ",
        "       |    ",
        "       |    ",
        "=========",
    ],
    [
        "   +---+    ",
        "   |   |    ",
        "   O   |    ",
        "  /|   |    ",
        "       |    ",
        "       |    ",
        "=========",
    ],
    [
        "   +---+    ",
        "   |   |    ",
        "   O   |    ",
        "  /|\\  |    ",
        "       |    ",
        "       |    ",
        "=========",
    ],
    [
        "   +---+    ",
        "   |   |    ",
        "   O   |    ",
        "  /|\\  |    ",
        "  /    |    ",
        "       |    ",
        "=========",
    ],
    [
        "   +---+    ",
        "   |   |    ",
        "   O   |    ",
        "  /|\\  |    ",
        "  / \\  |    ",
        "       |    ",
        "=========",
    ],
]

TITLE_BANNER = """
============================================================================
              🎮  H A N G M A N :  P R O   D A S H B O A R D  🎮             
============================================================================
"""

VICTORY_BANNER = """
  ★━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━★
    🎉  VICTORY! CONGRATULATIONS, YOU SAVED THE HANGMAN!  🎉
  ★━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━★
"""

DEFEAT_BANNER = """
  ☠━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━☠
    💀  GAME OVER! THE HANGMAN HAS FALLEN! BETTER LUCK NEXT TIME!  💀
  ☠━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━☠
"""


# ==============================================================================
# 3. DATA MODELS & STATS PERSISTENCE
# ==============================================================================

@dataclass
class WordEntry:
    """Represents a word in the game with its hint and category."""
    word: str
    hint: str
    category: str


@dataclass
class PlayerStats:
    """Tracks persistent session and all-time player performance."""
    games_played: int = 0
    wins: int = 0
    losses: int = 0
    current_streak: int = 0
    best_streak: int = 0
    words_solved: list[str] = field(default_factory=list)

    @property
    def win_rate(self) -> float:
        """Calculate player win percentage."""
        if self.games_played == 0:
            return 0.0
        return (self.wins / self.games_played) * 100.0


class StatsManager:
    """Handles loading and saving player statistics to disk."""

    def __init__(self, filepath: Path = STATS_FILE) -> None:
        self.filepath = filepath
        self.stats = self.load()

    def load(self) -> PlayerStats:
        """Load stats from JSON file or return fresh stats."""
        if self.filepath.exists():
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return PlayerStats(**data)
            except Exception:
                pass
        return PlayerStats()

    def save(self) -> None:
        """Persist stats to JSON file."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(asdict(self.stats), f, indent=2)
        except Exception:
            pass

    def record_game(self, won: bool, secret_word: str) -> None:
        """Record game result and update streaks."""
        self.stats.games_played += 1
        if won:
            self.stats.wins += 1
            self.stats.current_streak += 1
            if self.stats.current_streak > self.stats.best_streak:
                self.stats.best_streak = self.stats.current_streak
            if secret_word.upper() not in self.stats.words_solved:
                self.stats.words_solved.append(secret_word.upper())
        else:
            self.stats.losses += 1
            self.stats.current_streak = 0
        self.save()

    def reset(self) -> None:
        """Reset player stats."""
        self.stats = PlayerStats()
        self.save()


# ==============================================================================
# 4. WORD BANK
# ==============================================================================

class WordBank:
    """Manages categorized vocabulary and contextual hints."""

    CATEGORIES = {
        "1": {
            "name": "Programming (CodeAlpha Core)",
            "words": [
                WordEntry("python", "A popular interpreted language named after Monty Python", "Programming"),
                WordEntry("hangman", "The classic word-guessing game you are playing right now", "Programming"),
                WordEntry("developer", "A creative professional who builds software applications", "Programming"),
                WordEntry("keyboard", "Hardware peripheral used to type characters and commands", "Programming"),
                WordEntry("programming", "The craft of writing instructions for computers to execute", "Programming"),
                WordEntry("variable", "A named storage location in memory holding data values", "Programming"),
                WordEntry("algorithm", "A finite sequence of well-defined steps to solve a problem", "Programming"),
                WordEntry("terminal", "A text-based window used to run shell commands", "Programming"),
                WordEntry("function", "A reusable block of code designed to perform a single action", "Programming"),
                WordEntry("database", "An organized collection of data stored electronically", "Programming"),
            ],
        },
        "2": {
            "name": "Animals",
            "words": [
                WordEntry("dolphin", "Highly intelligent aquatic mammal famous for echolocation", "Animals"),
                WordEntry("elephant", "The largest living land animal, recognized by its long trunk", "Animals"),
                WordEntry("penguin", "Flightless bird thriving in Antarctic regions", "Animals"),
                WordEntry("cheetah", "The fastest land animal on Earth capable of high-speed sprints", "Animals"),
                WordEntry("kangaroo", "Australian marsupial known for powerful bounding hops", "Animals"),
                WordEntry("octopus", "Eight-armed marine mollusk with extraordinary camouflage skills", "Animals"),
                WordEntry("giraffe", "The tallest living terrestrial animal with an elongated neck", "Animals"),
            ],
        },
        "3": {
            "name": "Countries & Geography",
            "words": [
                WordEntry("canada", "Second-largest country by land area, home of the maple leaf", "Countries"),
                WordEntry("brazil", "Largest nation in South America, famous for the Amazon and football", "Countries"),
                WordEntry("japan", "East Asian island nation famed for cherry blossoms and technology", "Countries"),
                WordEntry("egypt", "Ancient civilization centered along the fertile banks of the Nile", "Countries"),
                WordEntry("germany", "European economic powerhouse famous for precision engineering", "Countries"),
                WordEntry("australia", "Vast island continent famous for the Great Barrier Reef", "Countries"),
            ],
        },
        "4": {
            "name": "Science & Universe",
            "words": [
                WordEntry("gravity", "Fundamental force pulling mass toward the center of planets", "Science"),
                WordEntry("galaxy", "Vast cosmic system of stars, stellar remnants, and dark matter", "Science"),
                WordEntry("molecule", "The smallest fundamental unit of a chemical compound", "Science"),
                WordEntry("photosynthesis", "Biological process converting light into chemical energy", "Science"),
                WordEntry("telescope", "Optical instrument enabling observation of distant celestial bodies", "Science"),
                WordEntry("quantum", "The minimum amount of any physical entity involved in an interaction", "Science"),
            ],
        },
    }

    @classmethod
    def get_category_choices(cls) -> list[tuple[str, str]]:
        """Return list of (key, display_name)."""
        choices = [(k, v["name"]) for k, v in cls.CATEGORIES.items()]
        choices.append(("5", "Random Mix (Any Category)"))
        return choices

    @classmethod
    def get_word(cls, category_key: str = "1") -> WordEntry:
        """Select a word entry based on category choice."""
        if category_key in cls.CATEGORIES:
            return random.choice(cls.CATEGORIES[category_key]["words"])
        # Random mix
        all_words: list[WordEntry] = []
        for cat in cls.CATEGORIES.values():
            all_words.extend(cat["words"])
        return random.choice(all_words)


# ==============================================================================
# 5. CORE GAME ENGINE
# ==============================================================================

class HangmanEngine:
    """State machine and logic engine for a single Hangman round."""

    def __init__(self, word_entry: WordEntry, difficulty: Difficulty = Difficulty.MEDIUM) -> None:
        self.word_entry = word_entry
        self.secret_word = word_entry.word.lower()
        self.hint = word_entry.hint
        self.category = word_entry.category
        self.difficulty = difficulty

        self.max_mistakes = difficulty.max_mistakes
        self.hints_allowed = difficulty.hints_allowed

        self.guessed_letters: set[str] = set()
        self.incorrect_guesses = 0
        self.hints_used = 0
        self.hint_revealed = False

    @property
    def remaining_lives(self) -> int:
        """Remaining incorrect guesses allowed."""
        return max(0, self.max_mistakes - self.incorrect_guesses)

    @property
    def is_won(self) -> bool:
        """Check if all unique letters in the secret word have been guessed."""
        return all(char == " " or char in self.guessed_letters for char in self.secret_word)

    @property
    def is_lost(self) -> bool:
        """Check if maximum allowed mistakes have been reached."""
        return self.incorrect_guesses >= self.max_mistakes

    @property
    def is_over(self) -> bool:
        """Check if game round has ended."""
        return self.is_won or self.is_lost

    def get_display_word(self, reveal_all: bool = False) -> str:
        """
        Return the secret word with guessed letters revealed and hidden letters as '_'.
        Matches CodeAlpha display requirements.
        """
        letters = []
        for char in self.secret_word:
            if char == " ":
                letters.append(" ")
            elif reveal_all or char in self.guessed_letters:
                letters.append(char)
            else:
                letters.append("_")
        return " ".join(letters)

    def guess_letter(self, letter: str) -> GuessResult:
        """Process a single letter guess."""
        char = letter.lower()

        if len(char) != 1 or not char.isalpha():
            return GuessResult.INVALID

        if char in self.guessed_letters:
            return GuessResult.ALREADY_TRIED

        self.guessed_letters.add(char)

        if char in self.secret_word:
            return GuessResult.CORRECT

        self.incorrect_guesses += 1
        return GuessResult.WRONG

    def guess_word(self, word: str) -> GuessResult:
        """Attempt to solve the entire word in one shot."""
        clean_word = word.strip().lower()
        if not clean_word.isalpha():
            return GuessResult.INVALID

        if clean_word == self.secret_word:
            for char in self.secret_word:
                self.guessed_letters.add(char)
            return GuessResult.SOLVED_WORD

        self.incorrect_guesses += 1
        return GuessResult.WRONG_WORD

    def request_hint(self) -> tuple[GuessResult, str]:
        """Request a contextual hint if allowed."""
        if self.hints_used >= self.hints_allowed:
            return GuessResult.HINT_EXHAUSTED, ""

        self.hints_used += 1
        self.hint_revealed = True
        return GuessResult.HINT_REVEALED, self.hint


# Backward-compatible standalone helper matching CodeAlpha specification
def display_word(secret_word: str, guessed_letters: list[str] | set[str]) -> str:
    """Show guessed letters and hide the rest with underscores."""
    shown_letters = []
    for letter in secret_word:
        if letter in guessed_letters:
            shown_letters.append(letter)
        else:
            shown_letters.append("_")
    return " ".join(shown_letters)


# ==============================================================================
# 6. DASHBOARD & UI RENDERER
# ==============================================================================

class DashboardRenderer:
    """Renders the visual ASCII dashboard, health bar, and alphabet tracker."""

    @staticmethod
    def clear_screen(enabled: bool = True) -> None:
        """Clear terminal screen if interactive and enabled."""
        if enabled and sys.stdout.isatty():
            os.system("cls" if os.name == "nt" else "clear")
        else:
            print("\n" + "-" * LINE_WIDTH)

    @staticmethod
    def format_health_bar(incorrect: int, max_mistakes: int) -> str:
        """Create a visual health meter bar."""
        remaining = max(0, max_mistakes - incorrect)
        filled = "■ " * remaining
        empty = "□ " * incorrect
        bar = f"[{filled}{empty}".rstrip() + "]"
        return f"{bar}  ({remaining}/{max_mistakes} lives left)"

    @staticmethod
    def format_alphabet_tracker(guessed_letters: set[str]) -> tuple[str, str]:
        """Return 2 rows of A-Z with tried letters bracketed."""
        upper_guessed = {l.upper() for l in guessed_letters}
        row1 = [f"[{c}]" if c in upper_guessed else f" {c} " for c in string.ascii_uppercase[:13]]
        row2 = [f"[{c}]" if c in upper_guessed else f" {c} " for c in string.ascii_uppercase[13:]]
        return " ".join(row1), " ".join(row2)

    @classmethod
    def get_stage_art(cls, incorrect: int, max_mistakes: int) -> list[str]:
        """Map mistakes count to available 7 ASCII stages."""
        if max_mistakes == 6:
            idx = min(incorrect, 6)
        else:
            # Scale proportionally to 0..6
            idx = int(round((incorrect / max_mistakes) * 6))
            idx = min(max(idx, 0), 6)
        return HANGMAN_STAGES_6[idx]

    @classmethod
    def render(
        cls,
        engine: HangmanEngine,
        stats: PlayerStats,
        status_message: str = "",
        clear: bool = True,
    ) -> None:
        """Render the complete unified dashboard."""
        cls.clear_screen(clear)
        print("=" * LINE_WIDTH)
        print("                🎮  H A N G M A N   D A S H B O A R D  🎮")
        print("=" * LINE_WIDTH)

        # Top Stats Bar
        print(
            f" [STATS] Games: {stats.games_played} | Wins: {stats.wins} | Losses: {stats.losses} | "
            f"Streak: {stats.current_streak} (Best: {stats.best_streak}) | Win Rate: {stats.win_rate:.1f}%"
        )
        print("-" * LINE_WIDTH)

        # Right-side details
        word_disp = engine.get_display_word()
        health_bar = cls.format_health_bar(engine.incorrect_guesses, engine.max_mistakes)
        tried_disp = ", ".join(sorted(engine.guessed_letters)) or "None"

        if engine.hint_revealed:
            hint_disp = f"💡 {engine.hint}"
        elif engine.hints_allowed > 0:
            hints_left = engine.hints_allowed - engine.hints_used
            hint_disp = f"[Type '?' for clue ({hints_left} remaining)]"
        else:
            hint_disp = "[Hints disabled in Hard mode]"

        right_side = [
            f"Category : {engine.category} ({engine.difficulty.display_name})",
            f"Word     : {word_disp}",
            f"",
            f"Health   : {health_bar}",
            f"Tried    : {tried_disp}",
            f"Hint     : {hint_disp}",
            f"Wrong guesses left: {engine.remaining_lives}/{engine.max_mistakes}",
        ]

        # Combine ASCII stage on left and text on right
        gallows = cls.get_stage_art(engine.incorrect_guesses, engine.max_mistakes)
        for left, right in zip(gallows, right_side):
            print(f"  {left:<15} │  {right}")

        print("-" * LINE_WIDTH)

        # Alphabet Tracker
        r1, r2 = cls.format_alphabet_tracker(engine.guessed_letters)
        print(" Alphabet Tracker (tried letters in brackets):")
        print(f"  {r1}")
        print(f"  {r2}")

        print("-" * LINE_WIDTH)
        if status_message:
            print(f" Status: {status_message}")
        else:
            print(" Status: Game in progress. Good luck!")
        print("=" * LINE_WIDTH)


# Standalone function matching CodeAlpha specification
def show_dashboard(
    secret_word: str,
    guessed_letters: list[str] | set[str],
    incorrect_guesses: int,
    max_incorrect: int = 6,
) -> None:
    """Show the current game status in a clean console panel."""
    print("\n" + "=" * 30)
    print("HANGMAN GAME")
    print("=" * 30)
    print(f"Word: {display_word(secret_word, guessed_letters)}")
    print(f"Letters tried: {', '.join(sorted(guessed_letters)) or 'None'}")
    print(f"Wrong guesses left: {max_incorrect - incorrect_guesses}/{max_incorrect}")
    print("=" * 30)


# ==============================================================================
# 7. CONTROLLER & APPLICATION FLOW
# ==============================================================================

class HangmanApp:
    """Main application controller managing CLI args, menus, and game rounds."""

    def __init__(self, clear_screen: bool = True, difficulty: Difficulty = Difficulty.MEDIUM) -> None:
        self.clear_screen = clear_screen
        self.difficulty = difficulty
        self.stats_manager = StatsManager()

    def select_category_interactive(self) -> str:
        """Interactive category selection menu."""
        DashboardRenderer.clear_screen(self.clear_screen)
        print("=" * LINE_WIDTH)
        print("                    SELECT WORD CATEGORY")
        print("=" * LINE_WIDTH)
        for key, name in WordBank.get_category_choices():
            print(f"  [{key}] {name}")
        print("=" * LINE_WIDTH)

        while True:
            choice = input("\nChoose a category (1-5, default 1): ").strip()
            if choice == "":
                return "1"
            if choice in ("1", "2", "3", "4", "5"):
                return choice
            print("Please enter a number between 1 and 5 (or press Enter for 1).")

    def select_difficulty_interactive(self) -> Difficulty:
        """Interactive difficulty selection."""
        DashboardRenderer.clear_screen(self.clear_screen)
        print("=" * LINE_WIDTH)
        print("                    SELECT DIFFICULTY")
        print("=" * LINE_WIDTH)
        print("  [1] Easy   - 8 Mistakes Allowed, 2 Clues")
        print("  [2] Medium - 6 Mistakes Allowed, 1 Clue (Standard CodeAlpha)")
        print("  [3] Hard   - 4 Mistakes Allowed, 0 Clues")
        print("=" * LINE_WIDTH)

        while True:
            choice = input("\nSelect difficulty (1-3, default 2): ").strip()
            if choice in ("", "2"):
                return Difficulty.MEDIUM
            if choice == "1":
                return Difficulty.EASY
            if choice == "3":
                return Difficulty.HARD
            print("Please choose 1, 2, or 3.")

    def get_player_guess(self, engine: HangmanEngine) -> tuple[str, str]:
        """Prompt and validate user input."""
        while True:
            raw = input("Your guess: ").strip().lower()

            if not raw:
                print("Please enter just one letter.")
                continue

            if raw in ("?", "hint"):
                return ("HINT", "")

            if len(raw) == 1:
                if not raw.isalpha():
                    print("Please enter just one letter.")
                    continue
                if raw in engine.guessed_letters:
                    print("You already tried that letter.")
                    continue
                return ("LETTER", raw)

            if raw.isalpha():
                return ("WORD", raw)

            print("Please enter just one letter.")

    def play_round(self, category_key: str = "1") -> bool:
        """Run one complete game round."""
        word_entry = WordBank.get_word(category_key)
        engine = HangmanEngine(word_entry, self.difficulty)
        status_msg = f"New round started! Category: {engine.category}"

        while not engine.is_over:
            DashboardRenderer.render(
                engine=engine,
                stats=self.stats_manager.stats,
                status_message=status_msg,
                clear=self.clear_screen,
            )

            action, value = self.get_player_guess(engine)

            if action == "HINT":
                res, hint_text = engine.request_hint()
                if res == GuessResult.HINT_REVEALED:
                    status_msg = f"Clue: {hint_text}"
                else:
                    status_msg = "No hints remaining for this difficulty!"

            elif action == "WORD":
                res = engine.guess_word(value)
                if res == GuessResult.SOLVED_WORD:
                    status_msg = f"Spot on! '{value.upper()}' is the correct word!"
                    break
                else:
                    status_msg = "That word isn't correct. That letter isn't in the word."

            elif action == "LETTER":
                res = engine.guess_letter(value)
                if res == GuessResult.CORRECT:
                    status_msg = "Good guess!"
                elif res == GuessResult.ALREADY_TRIED:
                    status_msg = "You already tried that letter."
                else:
                    status_msg = "That letter isn't in the word."

        # Update stats
        won = engine.is_won
        self.stats_manager.record_game(won, engine.secret_word)

        # Final screen display
        DashboardRenderer.render(
            engine=engine,
            stats=self.stats_manager.stats,
            status_message="Victory!" if won else "Game Over!",
            clear=self.clear_screen,
        )

        if won:
            print(VICTORY_BANNER)
            print(f"You got it! The word was {engine.secret_word}.")
        else:
            print(DEFEAT_BANNER)
            print(f"Out of guesses! The word was {engine.secret_word}.")

        return won

    def ask_play_again(self) -> bool:
        """Ask if player wants to play another round."""
        while True:
            ans = input("\nPlay again? (y/n): ").strip().lower()
            if ans in ("y", "yes"):
                return True
            if ans in ("n", "no"):
                return False
            print("Please answer y or n.")

    def show_session_summary(self) -> None:
        """Display player summary and leaderboard stats."""
        DashboardRenderer.clear_screen(self.clear_screen)
        stats = self.stats_manager.stats
        print("=" * LINE_WIDTH)
        print("               📊  FINAL PLAYER REPORT CARD  📊")
        print("=" * LINE_WIDTH)
        print(f"  • Total Games Played : {stats.games_played}")
        print(f"  • Victories          : {stats.wins}")
        print(f"  • Defeats            : {stats.losses}")
        print(f"  • Best Win Streak    : {stats.best_streak}")
        print(f"  • Win Percentage     : {stats.win_rate:.1f}%")
        if stats.words_solved:
            sample = ", ".join(stats.words_solved[-6:])
            print(f"  • Solved Vocabulary  : {sample}")
        print("=" * LINE_WIDTH)
        print("\nThanks for playing!")


# Backward-compatible helper matching CodeAlpha specification
def get_player_guess(guessed_letters: list[str] | set[str]) -> str:
    """Keep asking until the player enters a new single letter."""
    while True:
        guess = input("Your guess: ").strip().lower()
        if len(guess) != 1 or not guess.isalpha():
            print("Please enter just one letter.")
        elif guess in guessed_letters:
            print("You already tried that letter.")
        else:
            return guess


# Backward-compatible helper matching CodeAlpha specification
def play_game() -> None:
    """Play one basic round of Hangman."""
    app = HangmanApp()
    app.play_round("1")


# ==============================================================================
# 8. CLI & MAIN ENTRY POINT
# ==============================================================================

def build_parser() -> argparse.ArgumentParser:
    """Construct CLI argument parser for pro developer features."""
    parser = argparse.ArgumentParser(
        description="Hangman Pro - Production-grade CodeAlpha Task 1 Console Game"
    )
    parser.add_argument(
        "-d", "--difficulty",
        choices=["easy", "medium", "hard"],
        default="medium",
        help="Difficulty level (default: medium)",
    )
    parser.add_argument(
        "-c", "--category",
        choices=["1", "2", "3", "4", "5"],
        default=None,
        help="Category: 1=Programming, 2=Animals, 3=Countries, 4=Science, 5=Random",
    )
    parser.add_argument(
        "--no-clear",
        action="store_true",
        help="Disable console clearing (recommended for logging/automated tests)",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show persistent leaderboard stats and exit",
    )
    parser.add_argument(
        "--reset-stats",
        action="store_true",
        help="Reset stored high scores and exit",
    )
    return parser


def main() -> None:
    """Main entry point with CLI dispatch and clean exit guards."""
    parser = build_parser()
    args = parser.parse_args()

    # Stats display flags
    stats_mgr = StatsManager()
    if args.reset_stats:
        stats_mgr.reset()
        print("Statistics have been successfully reset.")
        return

    if args.stats:
        stats = stats_mgr.stats
        print("\n=== HANGMAN PRO CAREER STATS ===")
        print(f"Games: {stats.games_played} | Wins: {stats.wins} | Losses: {stats.losses}")
        print(f"Win Rate: {stats.win_rate:.1f}% | Best Streak: {stats.best_streak}")
        print(f"Solved Words: {len(stats.words_solved)}")
        return

    # Map difficulty
    diff_map = {
        "easy": Difficulty.EASY,
        "medium": Difficulty.MEDIUM,
        "hard": Difficulty.HARD,
    }
    difficulty = diff_map.get(args.difficulty, Difficulty.MEDIUM)

    app = HangmanApp(
        clear_screen=not args.no_clear,
        difficulty=difficulty,
    )

    print(TITLE_BANNER)
    print("Let's play Hangman!")

    try:
        # Category selection
        category_key = args.category if args.category else app.select_category_interactive()

        while True:
            app.play_round(category_key)

            if not app.ask_play_again():
                app.show_session_summary()
                break
    except (KeyboardInterrupt, EOFError):
        print("\n\nGame closed. Thanks for playing!")


if __name__ == "__main__":
    main()
