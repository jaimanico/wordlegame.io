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
    Returns a list of dicts: [{ 'letter': 'c', 'state': 'correct' }, ...]
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
            result[i] = {'letter': g, 'state': 'correct'}
        else:
            target_counts[t] = target_counts.get(t, 0) + 1

    # second pass: mark presents/absents
    for i, g in enumerate(guess):
        if result[i] is not None:
            continue
        if target_counts.get(g, 0) > 0:
            result[i] = {'letter': g, 'state': 'present'}
            target_counts[g] -= 1
        else:
            result[i] = {'letter': g, 'state': 'absent'}

    return result