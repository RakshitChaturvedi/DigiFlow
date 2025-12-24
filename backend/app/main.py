import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.db import base  # noqa: F401
from app.core.logging import setup_logging
from app.core.error_handlers import register_error_handlers
from app.core.middleware.request_id_middleware import RequestIDMiddleware
from app.core.middleware.tenant_middleware import TenantContextMiddleware
from app.api.v1.routers import (
    auth,
    test,
    users,
    products,
    machines,
    routings,
    orders,
)


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
app.add_middleware(TenantContextMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(test.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(products.router, prefix="/api/v1")
app.include_router(machines.router, prefix="/api/v1")
app.include_router(routings.router, prefix="/api/v1")
app.include_router(orders.router, prefix="/api/v1")


@app.get("/health")
def healt():
    return {"status": "ok"}
