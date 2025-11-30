import pytest

import game
from game import WordleGame, GuessFeedback


def test_evaluate_guess_handles_repeated_letters():
    feedback = game.evaluate_guess("civic", "cacao")

    assert feedback[0] == "correct"
    assert feedback.count("present") == 1
    assert feedback.count("correct") == 1


def test_wordle_game_marks_win_and_formats_feedback():
    wordle = WordleGame("apple")
    feedback = wordle.make_guess("apple")

    assert wordle.is_won is True
    assert wordle.is_game_over() is True
    assert all(entry["status"] == "correct" for entry in feedback)


def test_wordle_game_stores_guess_feedback_objects():
    wordle = WordleGame("candy")
    wordle.make_guess("cairn")

    assert isinstance(wordle.guesses[0], GuessFeedback)
    assert wordle.guesses[0].word == "cairn"


def test_load_words_filters_length(tmp_path):
    words_file = tmp_path / "words.txt"
    words_file.write_text("apple\npearl\nbananas\n")

    game.load_words.cache_clear()
    words = game.load_words(path=str(words_file), word_length=5)

    assert words == ["apple", "pearl"]

