# Wordle Web Application

A complete Wordle game implementation with Flask backend, SQLAlchemy models, and interactive frontend.

## 📋 Table of Contents
- [Features](#features)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Installation](#installation)
- [Running Locally](#running-locally)
- [Running with Docker](#running-with-docker)
- [Development](#development)

## 🌟 Features

- **Wordle Game Logic**: Complete implementation of Wordle rules with proper handling of repeated letters
- **Player Management**: Create and track players with their game statistics
- **Game Persistence**: SQLite database for storing games, players, and guesses
- **Responsive UI**: Clean, modern interface with color-coded feedback
- **API-Driven**: RESTful API serving both game logic and static assets
- **DevOps Ready**: Docker and Docker Compose configurations included

## 📂 Project Structure

```
wordle-project/
├── app.py                # Flask entry point with API endpoints
├── game.py               # Game logic and WordleGame class
├── models.py             # SQLAlchemy models (Player, Game, Guess)
├── requirements.txt      # Python dependencies
├── Dockerfile            # Container setup
├── docker-compose.yml    # Local run configuration
├── words.txt             # Word list for game targets
├── static/
│   ├── index.html        # Frontend UI
│   ├── script.js         # Frontend game logic
│   └── style.css         # Frontend styling
├── tests/
│   └── test_game.py      # Unit tests
└── .github/
    └── workflows/
        └── ci.yml        # GitHub Actions CI
```

## 🛠️ API Endpoints

- `GET /` - Serves the main HTML page
- `POST /api/players` - Create a new player
- `POST /api/games` - Start a new game
- `GET /api/games/<game_id>` - Get current game state
- `POST /api/games/<game_id>/guess` - Submit a guess
- `GET /api/leaderboard` - Get player leaderboard

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Docker and Docker Compose (optional)

### Setup
1. Clone the repository
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## ▶️ Running Locally

### Direct Python Execution
```bash
python app.py
```

The application will be available at `http://localhost:5000`

### With Gunicorn (Production)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🐳 Running with Docker

### Using Docker Compose (Recommended)
```bash
docker-compose up --build
```

The application will be available at `http://localhost:5000`

### Building and Running Manually
```bash
# Build the image
docker build -t wordle-app .

# Run the container
docker run -p 5000:5000 wordle-app
```

## 🧪 Testing

Run the unit tests:
```bash
pytest tests/
```

Run all tests with verbose output:
```bash
pytest tests/ -v
```

## 🔧 Development

The application is built with clean separation of concerns:
- **Game Logic**: `game.py` contains the `WordleGame` class and all game rules
- **Data Models**: `models.py` defines SQLAlchemy models for persistence
- **API Endpoints**: `app.py` provides the Flask application with all routes
- **Frontend**: Located in `static/` directory with HTML, CSS, and JavaScript
- **Tests**: Located in `tests/` directory with pytest configuration

## 📝 Technical Aspects

### Game Logic
- The `WordleGame` class manages game state, tracks guesses, and determines win conditions
- Feedback is provided for each letter: 'correct' (green), 'present' (yellow), 'absent' (gray)
- Proper handling of repeated letters according to Wordle rules

### Database Models
- `Player`: Tracks individual players with unique names
- `Game`: Represents a single game session with target word and win status
- `Guess`: Stores individual guesses made during a game with associated feedback

### Frontend Architecture
- Responsive design with CSS Grid and Flexbox
- Client-side JavaScript handles game state and API communication
- Color-coded feedback consistent with Wordle conventions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.