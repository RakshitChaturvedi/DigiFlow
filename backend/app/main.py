from fastapi import FastAPI

app = FastAPI(title="DigiFlow Backend", version="0.1.0")


@app.get("/health")
def healt():
    return {"status": "ok"}
