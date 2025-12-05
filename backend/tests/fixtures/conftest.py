import asyncio
import pytest
from typing import AsyncGenerator

from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from alembic import command
from alembic.config import Config

from app.main import app as real_app
from app.db.session import SessionLocal
from app.db.base import Base

# create seperate database
TEST_DATABASE_URL = "postgresql://postgres@localhost:5432/digiflow_test"

test_engine = create_engine(TEST_DATABASE_URL, future=True)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


# apply alembic migrations to test db
def run_migrations():
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    command.upgrade(alembic_cfg, "head")


# fixture: event loop for async tests
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


# override db dependency for tests
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# start test environment
@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    # drop and recreate db schema
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    run_migrations()

    # override db dependency
    real_app.dependency_overrides[SessionLocal] = TestingSessionLocal

    yield

    Base.metadata.drop_all(bind=test_engine)


# provide test client
@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=real_app, base_url="http://testserver") as ac:
        yield ac


# db sess for direct testing
@pytest.fixture
def db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# factory fixtures
@pytest.fixture
def create_user(db):
    # create user
    from app.models.user import User
    from app.core.security import hash_password

    def _create(
        email="test@example.com", password="password", role="manager", tenant_id=1
    ):
        user = User(
            email=email,
            tenant_id=tenant_id,
            hashed_password=hash_password(password),
            role=role,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    return _create


@pytest.fixture
def auth_headers(create_user, client, db):
    # return authz header for test user
    async def _headers():
        user = create_user()

        payload = {
            "email": user.email,
            "password": "password",
            "device_id": "test-device",
        }

        response = await client.post("/api/v1/auth/login", json=payload)
        token = response.json()["access_token"]

        return {"Authorization": f"Bearer {token}"}

    return _headers
