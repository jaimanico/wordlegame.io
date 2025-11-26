import json
import os
import time
from flask import Flask, Response, g, jsonify, request, send_from_directory
from flask_cors import CORS
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)

import game as game_logic
from constants import STATUS_CORRECT, WORD_LENGTH
from models import db, Player, Game, Guess


DEFAULT_DB_PATH = 'sqlite:///db.sqlite3'
APP_START_TIME = time.perf_counter()
REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total number of HTTP requests processed.",
    ["method", "endpoint", "http_status"],
)
REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds",
    "Request latency in seconds.",
    ["endpoint"],
)
ERROR_COUNT = Counter(
    "app_errors_total",
    "Total number of requests that raised an exception.",
    ["endpoint"],
)


def create_app(config_override=None):
    """Application factory to allow flexible configuration for tests and prod."""
    app = Flask(__name__)
    base_config = {
        'SQLALCHEMY_DATABASE_URI': os.environ.get('DB_PATH', DEFAULT_DB_PATH),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    }
    app.config.update(base_config)
    if config_override:
        app.config.update(config_override)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    CORS(app)
    _register_metrics(app)
    register_routes(app)
    return app


def register_routes(app):
    @app.route('/')
    def serve_index():
        return send_from_directory(os.path.join(app.root_path, 'static'), 'index.html')

    @app.route('/api/players', methods=['POST'])
    def create_player():
        data = request.get_json() or {}
        player_name = data.get('name') or data.get('player')

        if not player_name or not isinstance(player_name, str) or not player_name.strip():
            return jsonify({'error': 'player name required'}), 400

        player_name = player_name.strip()

        existing_player = Player.query.filter_by(name=player_name).first()
        if existing_player:
            return jsonify({'error': 'player already exists'}), 409

        new_player = Player(name=player_name)
        db.session.add(new_player)
        db.session.commit()

        return jsonify({'player': new_player.to_dict()}), 201

    @app.route('/api/games', methods=['POST'])
    def create_game():
        data = request.get_json() or {}
        player_name = data.get('player') or 'anonymous'
        if not isinstance(player_name, str) or not player_name.strip():
            return jsonify({'error': 'player name required'}), 400
        player_name = player_name.strip()

        player = Player.query.filter_by(name=player_name).first()
        if not player:
            player = Player(name=player_name)
            db.session.add(player)
            db.session.commit()

        target = game_logic.choose_word()
        new_game = Game(player_id=player.id, target_word=target)
        db.session.add(new_game)
        db.session.commit()

        guesses = _fetch_guess_history(new_game.id)

        return jsonify({'game': new_game.to_dict(), 'masked': '*' * WORD_LENGTH, 'guesses': guesses}), 201

    @app.route('/api/games/<int:game_id>', methods=['GET'])
    def get_game(game_id):
        game = Game.query.get_or_404(game_id)
        guesses = _fetch_guess_history(game.id)

        resp = game.to_dict()
        resp['guesses'] = guesses
        if game.finished:
            resp['target_word'] = game.target_word
        else:
            resp['target_word'] = None
        return jsonify(resp)

    @app.route('/api/games/<int:game_id>/guess', methods=['POST'])
    def submit_guess(game_id):
        data = request.get_json() or {}
        guess = (data.get('guess') or '').strip().lower()
        if len(guess) != WORD_LENGTH:
            return jsonify({'error': f'guess must be {WORD_LENGTH} letters'}), 400

        # Enforce that guesses must come from the same dictionary as target words
        # This prevents random 5-letter strings that are not in words.txt.
        valid_words = game_logic.load_words()
        if guess not in valid_words:
            return jsonify({'error': 'guess must be a valid word from the dictionary'}), 400

        game = Game.query.get_or_404(game_id)
        if game.finished:
            return jsonify({'error': 'game already finished'}), 400

        feedback = game_logic.evaluate_guess(game.target_word, guess)
        g = Guess(game_id=game.id, guess=guess, feedback=json.dumps(feedback))
        db.session.add(g)

        game.attempts += 1
        if all(p == STATUS_CORRECT for p in feedback):
            game.finished = True
            game.won = True
        elif game.attempts >= game.max_attempts:
            game.finished = True
            game.won = False

        db.session.commit()

        resp = g.to_dict()
        guesses = _fetch_guess_history(game.id)

        resp_game = game.to_dict()
        return jsonify({'guess': resp, 'game': resp_game, 'guesses': guesses}), 201

    @app.route('/api/leaderboard', methods=['GET'])
    def leaderboard():
        players = Player.query.all()
        board = []
        for p in players:
            total = Game.query.filter_by(player_id=p.id).count()
            wins = Game.query.filter_by(player_id=p.id, won=True).count()
            avg_attempts = None
            won_games = Game.query.filter_by(player_id=p.id, won=True).all()
            if won_games:
                avg_attempts = sum(g.attempts for g in won_games) / len(won_games)
            board.append({
                'player': p.name,
                'total_games': total,
                'wins': wins,
                'avg_attempts_for_wins': avg_attempts
            })
        board = sorted(board, key=lambda x: (-x['wins'], x['avg_attempts_for_wins'] or 999))
        return jsonify({'leaderboard': board})

    @app.route('/health')
    def health():
        uptime = time.perf_counter() - APP_START_TIME
        return jsonify({
            'status': 'ok',
            'uptime_seconds': round(uptime, 2),
            'timestamp': time.time(),
        })

    @app.route('/metrics')
    def metrics():
        return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


def _fetch_guess_history(game_id):
    guesses = Guess.query.filter_by(game_id=game_id).order_by(Guess.created_at).all()
    return [guess.to_dict() for guess in guesses]


def _register_metrics(app):
    @app.before_request
    def _start_timer():
        g.request_start_time = time.perf_counter()

    @app.after_request
    def _record_request(response):
        endpoint = request.endpoint or request.path
        latency = time.perf_counter() - g.get("request_start_time", time.perf_counter())
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            http_status=response.status_code,
        ).inc()
        return response

    @app.teardown_request
    def _track_errors(exc):
        if exc is not None:
            endpoint = request.endpoint or request.path
            ERROR_COUNT.labels(endpoint=endpoint).inc()


def _log_routes(app):
    print("==== Registered Flask routes ====")
    for rule in app.url_map.iter_rules():
        print(rule)
    print("=================================")


app = create_app()


if __name__ == '__main__':
    _log_routes(app)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
