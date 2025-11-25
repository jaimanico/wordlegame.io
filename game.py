import random
from dataclasses import dataclass
from functools import lru_cache
from typing import List

from constants import (
    DEFAULT_MAX_ATTEMPTS,
    FILE_ENCODING,
    STATUS_ABSENT,
    STATUS_CORRECT,
    STATUS_PRESENT,
    WORD_LENGTH,
    WORDS_FILE,
)


@lru_cache(maxsize=1)
def load_words(path: str = WORDS_FILE, word_length: int = WORD_LENGTH) -> List[str]:
    """Load and cache valid candidate words."""
    with open(path, "r", encoding=FILE_ENCODING) as words_file:
        normalized = [_normalize_word(line) for line in words_file if line.strip()]
    return [word for word in normalized if len(word) == word_length]


def choose_word(path: str = WORDS_FILE) -> str:
    """Return a random target word."""
    words = load_words(path)
    if not words:
        raise RuntimeError("words list is empty")
    return random.choice(words)


def evaluate_guess(target: str, guess: str) -> List[str]:
    """Return feedback list for each letter: 'correct', 'present', 'absent'."""
    normalized_target = _normalize_word(target)
    normalized_guess = _normalize_word(guess)
    _validate_word_length(normalized_target, "target")
    _validate_word_length(normalized_guess, "guess")

    result: List[str] = [None] * len(normalized_guess)
    target_counts = {}

    for index, (target_letter, guess_letter) in enumerate(
        zip(normalized_target, normalized_guess)
    ):
        if target_letter == guess_letter:
            result[index] = STATUS_CORRECT
        else:
            target_counts[target_letter] = target_counts.get(target_letter, 0) + 1

    for index, guess_letter in enumerate(normalized_guess):
        if result[index] is not None:
            continue
        if target_counts.get(guess_letter, 0) > 0:
            result[index] = STATUS_PRESENT
            target_counts[guess_letter] -= 1
        else:
            result[index] = STATUS_ABSENT

    return result


@dataclass
class GuessFeedback:
    """Encapsulates a single guess and its evaluation statuses."""

    word: str
    statuses: List[str]

    def is_correct(self) -> bool:
        return all(status == STATUS_CORRECT for status in self.statuses)

    def as_entries(self) -> List[dict]:
        return [
            {"letter": letter, "position": index, "status": status}
            for index, (letter, status) in enumerate(zip(self.word, self.statuses))
        ]


class WordleGame:
    """
    Class to handle a single Wordle game instance.
    
    Attributes:
        target_word (str): The word to be guessed
        guesses (list): List of guesses made so far
        max_attempts (int): Maximum number of allowed guesses (default 6)
        is_won (bool): Whether the game has been won
    """
    
    def __init__(self, target_word: str, max_attempts: int = DEFAULT_MAX_ATTEMPTS):
        """
        Initialize a Wordle game.
        
        Args:
            target_word (str): The word that needs to be guessed
            max_attempts (int): Maximum number of attempts allowed (default 6)
        """
        normalized_target = _normalize_word(target_word)
        _validate_word_length(normalized_target, "target")
        self.target_word = normalized_target
        self.guesses: List[GuessFeedback] = []
        self.max_attempts = max_attempts
        self.is_won = False
        
    def make_guess(self, guess_word: str):
        """
        Submit a guess and return feedback.
        
        Args:
            guess_word (str): The 5-letter word being guessed
            
        Returns:
            list: Feedback for each letter in the format 
                  [{'letter': 'A', 'position': 0, 'status': 'correct'}, ...]
        """
        normalized_guess = _normalize_word(guess_word)
        feedback_statuses = evaluate_guess(self.target_word, normalized_guess)

        guess_feedback = GuessFeedback(word=normalized_guess, statuses=feedback_statuses)
        self.guesses.append(guess_feedback)

        if guess_feedback.is_correct():
            self.is_won = True

        return guess_feedback.as_entries()
    
    def is_game_over(self):
        """
        Check if the game is over (either won or max attempts reached).
        
        Returns:
            bool: True if game is over, False otherwise
        """
        return self.is_won or len(self.guesses) >= self.max_attempts


def _normalize_word(word: str) -> str:
    return word.strip().lower()


def _validate_word_length(word: str, label: str, expected_length: int = WORD_LENGTH):
    if len(word) != expected_length:
        raise ValueError(f"{label} must be {expected_length} letters long")