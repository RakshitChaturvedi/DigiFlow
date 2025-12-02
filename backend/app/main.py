import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.db import base  # noqa: F401
from app.core.logging import setup_logging
from app.core.error_handlers import register_error_handlers
from app.core.middleware.request_id_middleware import RequestIDMiddleware
from app.core.middleware.tenant_middleware import TenantRLSMiddleware
from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.test import router as test_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(">>> Entering Lifespan startup")
    setup_logging()
    logger = logging.getLogger("uvicorn")
    logger.info("DigiFlow backend starting...")
    yield
    logger.info("DigiFlow backend shutting down...")
    print(">>> exiting lifespan shutdown")


app = FastAPI(lifespan=lifespan, title="DigiFlow Backend", version="0.1.0")

app.add_middleware(RequestIDMiddleware)
app.add_middleware(TenantRLSMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(test_router, prefix="/api/v1")


@app.get("/health")
def healt():
    return {"status": "ok"}
