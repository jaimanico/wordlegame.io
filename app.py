import os
import json
from flask import Flask, request, jsonify, abort
from models import db, Player, Game, Guess
import game as game_logic
from flask import send_from_directory
from flask_cors import CORS





DB_PATH = os.environ.get('DB_PATH', 'sqlite:///db.sqlite3')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB_PATH
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

@app.route('/')
def serve_index():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'index.html')

# initialize DB
db.init_app(app)
with app.app_context():
    db.create_all()

CORS(app)
@app.route('/api/games', methods=['POST'])
def create_game():
    data = request.get_json() or {}
    player_name = data.get('player') or 'anonymous'
    if not isinstance(player_name, str) or not player_name.strip():
        return jsonify({'error': 'player name required'}), 400
    player_name = player_name.strip()

    # find or create player
    player = Player.query.filter_by(name=player_name).first()
    if not player:
        player = Player(name=player_name)
        db.session.add(player)
        db.session.commit()

    target = game_logic.choose_word()
    new_game = Game(player_id=player.id, target_word=target)
    db.session.add(new_game)
    db.session.commit()

    return jsonify({'game': new_game.to_dict(), 'masked': '*****'}), 201


@app.route('/api/games/<int:game_id>', methods=['GET'])
def get_game(game_id):
    game = Game.query.get_or_404(game_id)
    guesses = [g.to_dict() for g in Guess.query.filter_by(game_id=game.id).order_by(Guess.created_at).all()]
    resp = game.to_dict()
    resp['guesses'] = guesses
    # do not reveal target_word unless finished (for dev only)
    if game.finished:
        resp['target_word'] = game.target_word
    else:
        resp['target_word'] = None
    return jsonify(resp)


@app.route('/api/games/<int:game_id>/guesses', methods=['POST'])
def submit_guess(game_id):
    data = request.get_json() or {}
    guess = (data.get('guess') or '').strip().lower()
    if len(guess) != 5:
        return jsonify({'error': 'guess must be 5 letters'}), 400

    game = Game.query.get_or_404(game_id)
    if game.finished:
        return jsonify({'error': 'game already finished'}), 400

    # evaluate
    feedback = game_logic.evaluate_guess(game.target_word, guess)
    g = Guess(game_id=game.id, guess=guess, feedback=json.dumps(feedback))
    db.session.add(g)

    game.attempts += 1
    # check win
    if all(p['state'] == 'correct' for p in feedback):
        game.finished = True
        game.won = True
    elif game.attempts >= game.max_attempts:
        game.finished = True
        game.won = False

    db.session.commit()

    resp = g.to_dict()
    resp_game = game.to_dict()
    return jsonify({'guess': resp, 'game': resp_game}), 201


@app.route('/api/leaderboard', methods=['GET'])
def leaderboard():
    # basic leaderboard: players sorted by wins desc
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


@app.route('/')
def index():
    return jsonify({'message': 'Wordle API — up and running'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)