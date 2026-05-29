"""
Fixtures compartidas entre todos los tests.

Estrategia de BD: SQLite en memoria con SQLAlchemy async.
No requiere PostgreSQL corriendo — los tests son completamente aislados.

Estrategia de SMS: MockSmsService que captura los códigos enviados,
inyectado via dependency_overrides de FastAPI.
"""
import os

# Deben estar antes de cualquier import de app para que Settings() no falle
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "clave-secreta-solo-para-tests-no-usar-en-prod")

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.database import Base
from app.main import app
from app.core.dependencies import get_db
from app.services.sms_service import SmsService, get_sms_service


# --- Mock SMS -----------------------------------------------------------

class MockSmsService(SmsService):
    """Captura los códigos en vez de enviarlos. Útil en tests."""

    def __init__(self):
        self.sent: list[dict] = []

    async def send_verification_code(self, phone_number: str, code: str) -> None:
        self.sent.append({"phone": phone_number, "code": code})

    def last_code_for(self, phone_number: str) -> str | None:
        for entry in reversed(self.sent):
            if entry["phone"] == phone_number:
                return entry["code"]
        return None


# --- BD en memoria -------------------------------------------------------

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def db_session():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


# --- Cliente HTTP de test ------------------------------------------------

@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):
    mock_sms = MockSmsService()

    async def override_get_db():
        yield db_session

    def override_get_sms():
        return mock_sms

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_sms_service] = override_get_sms

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac, mock_sms

    app.dependency_overrides.clear()
