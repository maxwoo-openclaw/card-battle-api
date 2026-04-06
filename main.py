import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import init_db, engine, Base
from app.routers import auth, cards, decks, matchmaking, users
from app.websocket.handlers import ws_game_handler
from app.services.card_service import CardService
from app.database import AsyncSessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: init DB and seed cards
    await init_db()
    async with AsyncSessionLocal() as db:
        service = CardService(db)
        await service.seed_sample_cards()
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="Card Battle API",
    description="A complete turn-based card battle game API with real-time WebSocket support",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(cards.router)
app.include_router(decks.router)
app.include_router(matchmaking.router)
app.include_router(users.router)


# Health check
@app.get("/health")
async def health():
    return {"status": "healthy", "app": "Card Battle API"}


# Root
@app.get("/")
async def root():
    return {
        "name": "Card Battle API",
        "version": "1.0.0",
        "docs": "/docs",
    }


# WebSocket endpoint
@app.websocket("/ws/game/{session_id}")
async def websocket_game(websocket: WebSocket, session_id: str):
    await ws_game_handler(websocket, session_id)


# Serve web app static files
web_dir = os.path.join(os.path.dirname(__file__), "web")
if os.path.exists(web_dir):
    app.mount("/web", StaticFiles(directory=web_dir, html=True), name="web")


# CLI-friendly run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
