import logging
from fastapi import FastAPI
from app.core.logging import setup_logging
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger = logging.getLogger("uvicorn")
    logger.info("DigiFlow backend starting...")
    yield
    logger.info("DigiFlow backend shutting down...")


app = FastAPI(lifespan=lifespan, title="DigiFlow Backend", version="0.1.0")


@app.get("/health")
def healt():
    return {"status": "ok"}
