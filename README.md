# 🃏 Card Battle Game API

A complete turn-based card battle game API with real-time WebSocket support and AI opponent.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green.svg)
![License](https://img.shields.io/badge/License-MIT-orange.svg)

## 🎮 Features

- **Card System** - 30+ cards across Monster, Spell, and Trap types
- **Turn-Based Combat** - Draw → Main → Battle → End phases
- **AI Opponent** - Three difficulty levels (Easy, Normal, Hard)
- **Real-time WebSocket** - Instant game state updates
- **JWT Authentication** - Secure user accounts and deck management
- **Deck Building** - Create custom decks with deck validation

## 🔧 Tech Stack

- **Backend**: Python 3.11+ / FastAPI
- **Database**: SQLite (development)
- **WebSocket**: Native FastAPI WebSocket
- **Auth**: JWT (python-jose)
- **ORM**: SQLAlchemy (async)

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/maxwoo-openclaw/card-battle-api.git
cd card-battle-api

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --host 0.0.0.0 --port 8000
```

## 🌐 Access

- **Web App**: http://localhost:8000/web/index.html
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🎯 Quick Start

1. Register an account at `/api/auth/register`
2. Login to get JWT token
3. Create a deck with `/api/decks`
4. Start a game vs AI at `/api/matchmaking/vs-ai`
5. Connect via WebSocket at `/ws/game/{session_id}`

## 📁 Project Structure

```
card_battle_api/
├── main.py                 # FastAPI entry point
├── requirements.txt        # Dependencies
├── app/
│   ├── config.py          # Configuration
│   ├── database.py        # SQLAlchemy setup
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   ├── routers/           # API endpoints
│   ├── services/           # Business logic
│   │   ├── ai_opponent.py # AI opponent logic
│   │   └── game_logic.py  # Game rules
│   ├── websocket/          # WebSocket handlers
│   └── utils/             # Security & utilities
├── web/
│   └── index.html          # Web client (SPA)
└── tests/                 # Unit tests
```

## 🃏 Card Types

| Type | Description |
|------|-------------|
| **Monster** | Attack and defense units |
| **Spell** | Instant effects |
| **Trap** | Triggered effects |

## ⚔️ Combat System

- Each player starts with **1000 HP**
- **Energy** increases by 1 per turn (max 10)
- **Win condition**: Reduce opponent HP to 0

## 🤖 AI Difficulty

| Level | Behavior |
|-------|----------|
| **Easy** | Random card selection and attacks |
| **Normal** | Value-based decisions, prioritizes kills |
| **Hard** | Board evaluation, plans ahead |

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Current user

### Cards
- `GET /api/cards` - List all cards
- `GET /api/cards/{id}` - Card details

### Decks
- `GET /api/decks` - List user decks
- `POST /api/decks` - Create deck
- `PUT /api/decks/{id}` - Update deck
- `DELETE /api/decks/{id}` - Delete deck

### Matchmaking
- `POST /api/matchmaking/vs-ai?deck_id=X&difficulty=Y` - Start vs AI game

## 🧪 Run Tests

```bash
python -m pytest tests/ -v
```

## 📝 License

MIT License
