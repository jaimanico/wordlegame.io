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
│   ├── conftest.py       # pytest fixtures
│   ├── test_app_integration.py
│   ├── test_game_logic.py
│   ├── test_game.py
│   └── test_models.py
├── scripts/
│   └── deploy.sh         # Deployment helper used by CI/CD
└── .github/
    └── workflows/
        └── ci.yml        # GitHub Actions CI/CD
```

## 🛠️ API Endpoints

- `GET /` - Serves the main HTML page
- `POST /api/players` - Create a new player
- `POST /api/games` - Start a new game
- `GET /api/games/<game_id>` - Get current game state
- `POST /api/games/<game_id>/guess` - Submit a guess
- `GET /api/leaderboard` - Get player leaderboard
- `GET /health` - Lightweight health check with uptime metadata
- `GET /metrics` - Prometheus-formatted metrics (requests, latency, errors)

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

Run the automated test suite with coverage (fails if <70%):
```bash
pytest --cov=. --cov-report=term --cov-report=xml --cov-report=html:reports/htmlcov
coverage report --fail-under=70
```

Coverage artifacts are written to `.coverage`, `coverage.xml`, and `reports/htmlcov` (all gitignored).

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

## ⚙️ CI/CD

- **Location:** `.github/workflows/ci.yml`
- **Triggers:** pushes & pull requests targeting `main` or `develop`
- **Steps:**
  1. Install dependencies.
  2. Run `pytest` with coverage; pipeline fails if coverage drops below 70%.
  3. Upload coverage artifacts.
  4. Authenticate against GitHub Container Registry (GHCR), build the Docker image, and push on direct pushes.
  5. Deploy job runs only for pushes to `main`; it reuses the built image and invokes `scripts/deploy.sh`.

### Required secrets

| Secret | Purpose |
| ------ | ------- |
| `DEPLOY_WEBHOOK_URL` | HTTPS endpoint that triggers the cloud deployment (Render, Fly.io, etc.). |
| `DEPLOY_PAYLOAD` *(optional)* | Extra payload sent to the webhook for custom automation. |

The workflow already uses `GITHUB_TOKEN` for GHCR access, so no extra registry secrets are required unless you switch registries.

Only the `main` branch deploys automatically; other branches still run the CI portion (tests + docker build).

## 📈 Monitoring & Health

- `/health` returns JSON with `status`, `uptime_seconds`, and the current timestamp. Use this for readiness/liveness probes.
- `/metrics` exposes Prometheus metrics. Out of the box it exports:
  - `app_requests_total{method,endpoint,http_status}`
  - `app_request_latency_seconds{endpoint}`
  - `app_errors_total{endpoint}`
- Minimal Prometheus setup is provided at `monitoring/prometheus.yml`. Point the `targets` entry to wherever the app runs (default `localhost:5000`). Example usage:

  ```bash
  prometheus --config.file=monitoring/prometheus.yml
  ```

- Once Prometheus is scraping `/metrics`, you can plug it into Grafana and create panels for request rate, P95 latency, etc. A simple Grafana dashboard can query:
  - `rate(app_requests_total[5m])` for QPS
  - `histogram_quantile(0.95, sum(rate(app_request_latency_seconds_bucket[5m])) by (le))` for latency
  - `rate(app_errors_total[5m])` for error trends

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.