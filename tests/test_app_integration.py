from constants import STATUS_CORRECT, WORD_LENGTH
from models import Game, Guess, Player


def test_create_player_and_prevent_duplicates(client, app_instance):
    resp = client.post('/api/players', json={'name': 'integration'})
    assert resp.status_code == 201

    duplicate = client.post('/api/players', json={'name': 'integration'})
    assert duplicate.status_code == 409

    with app_instance.app_context():
        assert Player.query.count() == 1


def test_game_flow_and_leaderboard(client, app_instance, monkeypatch):
    monkeypatch.setattr('app.game_logic.choose_word', lambda: 'apple')

    create_resp = client.post('/api/games', json={'player': 'integration'})
    assert create_resp.status_code == 201
    game_payload = create_resp.get_json()['game']
    game_id = game_payload['id']

    guess_resp = client.post(f'/api/games/{game_id}/guess', json={'guess': 'apple'})
    assert guess_resp.status_code == 201
    guess_data = guess_resp.get_json()

    assert guess_data['game']['finished'] is True
    assert guess_data['game']['won'] is True
    assert guess_data['guess']['feedback'] == [STATUS_CORRECT] * WORD_LENGTH

    detail_resp = client.get(f'/api/games/{game_id}')
    assert detail_resp.status_code == 200
    assert detail_resp.get_json()['target_word'] == 'apple'

    leaderboard = client.get('/api/leaderboard')
    assert leaderboard.status_code == 200
    board = leaderboard.get_json()['leaderboard']
    assert board[0]['wins'] == 1

    with app_instance.app_context():
        assert Game.query.count() == 1
        assert Guess.query.count() == 1

