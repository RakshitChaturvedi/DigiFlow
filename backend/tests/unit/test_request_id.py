from fastapi import FastAPI

from starlette.requests import Request
from starlette.testclient import TestClient

from app.core.middleware.request_id_middleware import RequestIDMiddleware


def test_request_id_injected():
    app = FastAPI()
    app.add_middleware(RequestIDMiddleware)

    @app.get("/test")
    def test(request: Request):
        return {"request_id": request.state.request_id}

    client = TestClient(app)
    res = client.get("/test")

    assert "request_id" in res.json()
    assert isinstance(res.json()["request_id"], str)
