"""Tests del catálogo de lecciones y disponibilidad por prerequisito."""
import pytest
from httpx import AsyncClient

from tests.conftest import create_test_user, create_test_lesson, auth_headers
from app.models.content import ContentArea, ModuleType


@pytest.mark.asyncio
async def test_catalog_requires_valid_user(client):
    ac, _ = client
    from app.core.security import create_access_token
    import uuid
    # Token válido pero el user_id no existe en BD → 401
    token = create_access_token(uuid.uuid4())
    resp = await ac.get("/lessons", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_catalog_returns_lessons(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    await create_test_lesson(db_session, title="WhatsApp básico")
    await create_test_lesson(db_session, title="Fotos en WhatsApp", order_index=1)

    resp = await ac.get("/lessons", headers=auth_headers(user))

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["title"] == "WhatsApp básico"


@pytest.mark.asyncio
async def test_catalog_filter_by_area(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    await create_test_lesson(db_session, content_area=ContentArea.comunicacion)
    await create_test_lesson(db_session, content_area=ContentArea.banca)

    resp = await ac.get("/lessons?content_area=comunicacion", headers=auth_headers(user))

    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["content_area"] == "comunicacion"


@pytest.mark.asyncio
async def test_lesson_without_prerequisite_is_available(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    lesson = await create_test_lesson(db_session)

    resp = await ac.get(f"/lessons/{lesson.id}", headers=auth_headers(user))

    assert resp.status_code == 200
    assert resp.json()["is_available"] is True


@pytest.mark.asyncio
async def test_lesson_with_unmet_prerequisite_is_unavailable(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    first = await create_test_lesson(db_session, title="Primera")
    second = await create_test_lesson(db_session, title="Segunda", prerequisite_id=first.id)

    resp = await ac.get(f"/lessons/{second.id}", headers=auth_headers(user))

    assert resp.status_code == 200
    assert resp.json()["is_available"] is False


@pytest.mark.asyncio
async def test_lesson_not_found_returns_404(client, db_session):
    ac, _ = client
    import uuid
    user = await create_test_user(db_session)

    resp = await ac.get(f"/lessons/{uuid.uuid4()}", headers=auth_headers(user))

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_catalog_shows_progress(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    lesson = await create_test_lesson(db_session)

    # Inicia la lección para generar progreso
    await ac.post(f"/progress/{lesson.id}/start", headers=auth_headers(user))
    await ac.patch(
        f"/progress/{lesson.id}",
        json={"completion_pct": 50},
        headers=auth_headers(user),
    )

    resp = await ac.get("/lessons", headers=auth_headers(user))
    item = resp.json()[0]
    assert item["completion_pct"] == 50
    assert item["completed"] is False
