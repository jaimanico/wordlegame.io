import random
import json
from functools import lru_cache

WORDS_FILE = 'words.txt'

@lru_cache(maxsize=1)
def load_words(path=WORDS_FILE):
    with open(path, 'r', encoding='utf-8') as f:
        words = [w.strip().lower() for w in f if w.strip()]
    # keep only 5-letter words
    words = [w for w in words if len(w) == 5]
    return words


def choose_word(path=WORDS_FILE):
    words = load_words(path)
    if not words:
        raise RuntimeError('words list is empty')
    return random.choice(words)


def evaluate_guess(target: str, guess: str):
    """Return feedback list for each letter: 'correct', 'present', 'absent'

    Implements Wordle rules with proper handling of repeated letters.
    Returns a list of states: ['correct', 'present', 'absent', ...]
    """
    target = target.lower()
    guess = guess.lower()
    if len(target) != len(guess):
        raise ValueError('target and guess must be same length')

    result = [None] * len(guess)
    target_counts = {}

    # first pass: mark corrects
    for i, (t, g) in enumerate(zip(target, guess)):
        if t == g:
            result[i] = 'correct'
        else:
            target_counts[t] = target_counts.get(t, 0) + 1

    # second pass: mark presents/absents
    for i, g in enumerate(guess):
        if result[i] is not None:
            continue
        if target_counts.get(g, 0) > 0:
            result[i] = 'present'
            target_counts[g] -= 1
        else:
            result[i] = 'absent'

    return result


class WordleGame:
    """
    Class to handle a single Wordle game instance.
    
    Attributes:
        target_word (str): The word to be guessed
        guesses (list): List of guesses made so far
        max_attempts (int): Maximum number of allowed guesses (default 6)
        is_won (bool): Whether the game has been won
    """
    
    def __init__(self, target_word: str, max_attempts: int = 6):
        """
        Initialize a Wordle game.
        
        Args:
            target_word (str): The word that needs to be guessed
            max_attempts (int): Maximum number of attempts allowed (default 6)
        """
        self.target_word = target_word.lower()
        self.guesses = []
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
        guess_word = guess_word.lower()
        feedback = evaluate_guess(self.target_word, guess_word)
        
        # Store the guess with its feedback
        guess_entry = {
            'word': guess_word,
            'feedback': feedback
        }
        self.guesses.append(guess_entry)
        
        # Check if the guess was correct
        if all(status == 'correct' for status in feedback):
            self.is_won = True
            
        # Format feedback in the expected structure for the frontend
        formatted_feedback = []
        for i, (letter, status) in enumerate(zip(guess_word, feedback)):
            formatted_feedback.append({
                'letter': letter,
                'position': i,
                'status': status
            })
            
        return formatted_feedback
    
    def is_game_over(self):
        """
        Check if the game is over (either won or max attempts reached).
        
        Returns:
            bool: True if game is over, False otherwise
        """
        return self.is_won or len(self.guesses) >= self.max_attempts