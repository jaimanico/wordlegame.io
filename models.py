from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Player(db.Model):
    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "created_at": self.created_at.isoformat()}

class Game(db.Model):
    __tablename__ = 'games'
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'), nullable=False)
    target_word = db.Column(db.String(5), nullable=False)
    attempts = db.Column(db.Integer, default=0)
    max_attempts = db.Column(db.Integer, default=6)
    finished = db.Column(db.Boolean, default=False)
    won = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    player = db.relationship('Player', backref=db.backref('games', lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "player_id": self.player_id,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "finished": self.finished,
            "won": self.won,
            "created_at": self.created_at.isoformat()
        }

class Guess(db.Model):
    __tablename__ = 'guesses'
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    guess = db.Column(db.String(5), nullable=False)
    feedback = db.Column(db.Text, nullable=False)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    game = db.relationship('Game', backref=db.backref('guesses', lazy=True))

    def to_dict(self):
        import json
        try:
            feedback_parsed = json.loads(self.feedback)
        except Exception:
            feedback_parsed = []
        return {
            "id": self.id,
            "game_id": self.game_id,
            "guess": self.guess,
            "feedback": feedback_parsed,
            "created_at": self.created_at.isoformat()
        }