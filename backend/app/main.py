from fastapi import FastAPI
from backend.app.api.players import router as players_router

app = FastAPI(
    title="RosterPulse API",
    version="0.1.0"
)

app.include_router(players_router)

@app.get("/")
def root():
    return {
        "app": "RosterPulse",
        "status": "running"
    }