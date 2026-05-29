"""
Fixtures compartidas entre todos los tests.

Estrategia de BD: SQLite en memoria con SQLAlchemy async.
No requiere PostgreSQL corriendo — los tests son completamente aislados.

Estrategia de SMS: MockSmsService que captura los códigos enviados,
inyectado via dependency_overrides de FastAPI.
"""
import os
import uuid

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
from app.core.security import create_access_token
from app.services.sms_service import SmsService, get_sms_service
from app.services.pdf_service import PdfService, get_pdf_service
from app.models.user import User
from app.models.content import Lesson, ModuleType, ContentArea, SimulatorCatalog
from app.models.achievement import Achievement, TriggerType


# --- Mock SMS -----------------------------------------------------------

class MockSmsService(SmsService):
    """Captura los códigos en vez de enviarlos."""

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

class MockPdfService(PdfService):
    async def generate_graduation_summary(self, data: dict) -> str:
        return f"summaries/mock_graduacion_{data['user_id']}.pdf"


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):
    mock_sms = MockSmsService()
    mock_pdf = MockPdfService()

    async def override_get_db():
        yield db_session

    def override_get_sms():
        return mock_sms

    def override_get_pdf():
        return mock_pdf

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_sms_service] = override_get_sms
    app.dependency_overrides[get_pdf_service] = override_get_pdf

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac, mock_sms

    app.dependency_overrides.clear()


# --- Helpers de datos de prueba -----------------------------------------

PHONE = "+56912345678"


async def create_test_user(db: AsyncSession, phone: str = PHONE) -> User:
    user = User(phone_number=phone, phone_verified=True)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


def auth_headers(user: User) -> dict:
    token = create_access_token(user.id)
    return {"Authorization": f"Bearer {token}"}


async def create_test_lesson(
    db: AsyncSession,
    *,
    title: str = "Lección de prueba",
    content_area: ContentArea = ContentArea.comunicacion,
    module_type: ModuleType = ModuleType.guide,
    prerequisite_id: uuid.UUID | None = None,
    order_index: int = 0,
) -> Lesson:
    lesson = Lesson(
        title=title,
        content_area=content_area,
        module_type=module_type,
        duration_minutes=8,
        prerequisite_id=prerequisite_id,
        order_index=order_index,
        is_published=True,
    )
    db.add(lesson)
    await db.commit()
    await db.refresh(lesson)
    return lesson


async def create_test_achievement(
    db: AsyncSession,
    *,
    key: str = "test_achievement",
    trigger_type: TriggerType = TriggerType.lesson_count,
    content_area: str | None = None,
    threshold: int = 1,
) -> Achievement:
    achievement = Achievement(
        key=key,
        trigger_type=trigger_type,
        content_area=content_area,
        threshold=threshold,
    )
    db.add(achievement)
    await db.commit()
    await db.refresh(achievement)
    return achievement


async def create_test_simulator(
    db: AsyncSession,
    *,
    slug: str = "whatsapp",
    title: str = "WhatsApp",
    content_area: ContentArea = ContentArea.comunicacion,
    module_type: ModuleType = ModuleType.simulator,
) -> SimulatorCatalog:
    simulator = SimulatorCatalog(
        slug=slug,
        title=title,
        content_area=content_area,
        module_type=module_type,
        is_active=True,
    )
    db.add(simulator)
    await db.commit()
    await db.refresh(simulator)
    return simulator
