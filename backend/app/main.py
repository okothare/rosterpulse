from fastapi import FastAPI

app = FastAPI(
    title="RosterPulse API",
    version="0.1.0"
)

@app.get("/")
def root():
    return {
        "app": "RosterPulse",
        "status": "running"
    }