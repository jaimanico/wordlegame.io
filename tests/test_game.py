import pytest
from game import WordleGame

def test_new_game_starts_with_empty_guesses():
    game = WordleGame("apple")
    assert game.guesses == []

def test_correct_guess_wins():
    game = WordleGame("apple")
    feedback = game.make_guess("apple")
    assert game.is_won is True
    assert all(f["status"] == "correct" for f in feedback)

def test_incorrect_guess_gives_feedback():
    game = WordleGame("apple")
    feedback = game.make_guess("grape")
    assert len(feedback) == 5
    # Make sure at least one letter is marked (present or correct)
    assert any(f["status"] in ("correct", "present") for f in feedback)
