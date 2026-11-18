"""
Unit test suite for Hangman Pro
Tests engine logic, input handling, win/loss states, and stats manager.
"""

import unittest
from pathlib import Path
import tempfile

from main import (
    Difficulty,
    GuessResult,
    HangmanEngine,
    PlayerStats,
    StatsManager,
    WordBank,
    WordEntry,
    display_word,
)


class TestWordBank(unittest.TestCase):
    """Test WordBank category loading and retrieval."""

    def test_default_categories_exist(self):
        choices = WordBank.get_category_choices()
        self.assertGreaterEqual(len(choices), 4)

    def test_word_selection(self):
        entry = WordBank.get_word("1")
        self.assertIsInstance(entry, WordEntry)
        self.assertTrue(len(entry.word) >= 3)
        self.assertTrue(len(entry.hint) > 0)


class TestHangmanEngine(unittest.TestCase):
    """Test state machine and game rules."""

    def setUp(self):
        self.entry = WordEntry("python", "A snake-themed programming language", "Programming")
        self.engine = HangmanEngine(self.entry, Difficulty.MEDIUM)

    def test_initial_state(self):
        self.assertEqual(self.engine.incorrect_guesses, 0)
        self.assertEqual(self.engine.remaining_lives, 6)
        self.assertFalse(self.engine.is_won)
        self.assertFalse(self.engine.is_lost)
        self.assertEqual(self.engine.get_display_word(), "_ _ _ _ _ _")

    def test_correct_guess(self):
        res = self.engine.guess_letter("p")
        self.assertEqual(res, GuessResult.CORRECT)
        self.assertIn("p", self.engine.guessed_letters)
        self.assertEqual(self.engine.incorrect_guesses, 0)
        self.assertEqual(self.engine.remaining_lives, 6)
        self.assertEqual(self.engine.get_display_word(), "p _ _ _ _ _")

    def test_wrong_guess(self):
        res = self.engine.guess_letter("z")
        self.assertEqual(res, GuessResult.WRONG)
        self.assertIn("z", self.engine.guessed_letters)
        self.assertEqual(self.engine.incorrect_guesses, 1)
        self.assertEqual(self.engine.remaining_lives, 5)

    def test_repeated_guess(self):
        self.engine.guess_letter("p")
        res = self.engine.guess_letter("p")
        self.assertEqual(res, GuessResult.ALREADY_TRIED)
        self.assertEqual(self.engine.incorrect_guesses, 0)

    def test_invalid_guess(self):
        res = self.engine.guess_letter("9")
        self.assertEqual(res, GuessResult.INVALID)
        res_empty = self.engine.guess_letter("")
        self.assertEqual(res_empty, GuessResult.INVALID)
        self.assertEqual(self.engine.incorrect_guesses, 0)

    def test_full_word_solve_correct(self):
        res = self.engine.guess_word("python")
        self.assertEqual(res, GuessResult.SOLVED_WORD)
        self.assertTrue(self.engine.is_won)
        self.assertFalse(self.engine.is_lost)
        self.assertEqual(self.engine.get_display_word(), "p y t h o n")

    def test_full_word_solve_wrong(self):
        res = self.engine.guess_word("java")
        self.assertEqual(res, GuessResult.WRONG_WORD)
        self.assertEqual(self.engine.incorrect_guesses, 1)

    def test_loss_condition(self):
        for char in ["a", "b", "c", "d", "e", "f"]:
            self.engine.guess_letter(char)
        self.assertTrue(self.engine.is_lost)
        self.assertFalse(self.engine.is_won)
        self.assertEqual(self.engine.remaining_lives, 0)

    def test_hint_system(self):
        res, hint_text = self.engine.request_hint()
        self.assertEqual(res, GuessResult.HINT_REVEALED)
        self.assertEqual(hint_text, self.entry.hint)

        # In medium, only 1 hint is allowed
        res2, _ = self.engine.request_hint()
        self.assertEqual(res2, GuessResult.HINT_EXHAUSTED)


class TestStatsManager(unittest.TestCase):
    """Test JSON persistence and streak calculation."""

    def test_stats_recording(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            mgr = StatsManager(tmp_path)
            self.assertEqual(mgr.stats.games_played, 0)

            mgr.record_game(won=True, secret_word="python")
            self.assertEqual(mgr.stats.games_played, 1)
            self.assertEqual(mgr.stats.wins, 1)
            self.assertEqual(mgr.stats.current_streak, 1)
            self.assertEqual(mgr.stats.best_streak, 1)

            mgr.record_game(won=False, secret_word="hangman")
            self.assertEqual(mgr.stats.games_played, 2)
            self.assertEqual(mgr.stats.losses, 1)
            self.assertEqual(mgr.stats.current_streak, 0)
            self.assertEqual(mgr.stats.best_streak, 1)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()


class TestLegacyCompatibility(unittest.TestCase):
    """Ensure original CodeAlpha function names and behaviors remain 100% compatible."""

    def test_display_word_standalone(self):
        res = display_word("python", ["p", "o"])
        self.assertEqual(res, "p _ _ _ o _")


if __name__ == "__main__":
    unittest.main()
