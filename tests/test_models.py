from datetime import datetime, timezone

from models import Guess


def test_guess_to_dict_parses_feedback_json():
    guess = Guess(
        game_id=1,
        guess="crane",
        feedback='["correct","present","absent","absent","present"]',
        created_at=datetime.now(timezone.utc),
    )

    payload = guess.to_dict()
    assert payload["feedback"][0] == "correct"
    assert payload["guess"] == "crane"


def test_guess_to_dict_handles_invalid_feedback():
    guess = Guess(
        game_id=1,
        guess="crane",
        feedback="not-json",
        created_at=datetime.now(timezone.utc),
    )

    payload = guess.to_dict()
    assert payload["feedback"] == []

