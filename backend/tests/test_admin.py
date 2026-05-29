"""Tests de endpoints protegidos del área de administración."""
import pytest

from tests.conftest import (
    create_test_admin, create_test_user, create_test_simulator,
    admin_token_headers, auth_headers,
)


@pytest.mark.asyncio
async def test_admin_stats_requires_auth(client, db_session):
    ac, _ = client
    resp = await ac.get("/admin/stats")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_admin_stats_returns_data(client, db_session):
    ac, _ = client
    admin = await create_test_admin(db_session)
    await create_test_user(db_session)

    resp = await ac.get("/admin/stats", headers=admin_token_headers(admin))

    assert resp.status_code == 200
    data = resp.json()
    assert data["total_users"] == 1
    assert "total_requests" in data
    assert "active_simulators" in data


@pytest.mark.asyncio
async def test_admin_list_users(client, db_session):
    ac, _ = client
    admin = await create_test_admin(db_session)
    await create_test_user(db_session, phone="+56911111111")
    await create_test_user(db_session, phone="+56922222222")

    resp = await ac.get("/admin/users", headers=admin_token_headers(admin))

    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_admin_update_request_status(client, db_session):
    ac, _ = client
    admin = await create_test_admin(db_session)
    user = await create_test_user(db_session)

    # Crear petición directamente
    from app.models.community import LearningRequest, RequestStatus
    req = LearningRequest(user_id=user.id, description="Quiero aprender a usar el correo")
    db_session.add(req)
    await db_session.commit()
    await db_session.refresh(req)

    resp = await ac.patch(
        f"/admin/requests/{req.id}/status",
        json={"status": "in_development"},
        headers=admin_token_headers(admin),
    )

    assert resp.status_code == 200
    assert resp.json()["status"] == "in_development"


@pytest.mark.asyncio
async def test_admin_update_request_status_nonexistent_returns_404(client, db_session):
    ac, _ = client
    admin = await create_test_admin(db_session)
    import uuid

    resp = await ac.patch(
        f"/admin/requests/{uuid.uuid4()}/status",
        json={"status": "available"},
        headers=admin_token_headers(admin),
    )

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_admin_create_simulator(client, db_session):
    ac, _ = client
    admin = await create_test_admin(db_session)

    resp = await ac.post(
        "/admin/simulators",
        json={
            "slug": "correo_electronico",
            "title": "Correo electrónico",
            "module_type": "simulator",
            "content_area": "comunicacion",
            "difficulty": 2,
        },
        headers=admin_token_headers(admin),
    )

    assert resp.status_code == 201
    assert resp.json()["slug"] == "correo_electronico"


@pytest.mark.asyncio
async def test_admin_create_simulator_duplicate_slug_returns_409(client, db_session):
    ac, _ = client
    admin = await create_test_admin(db_session)
    await create_test_simulator(db_session, slug="whatsapp")

    resp = await ac.post(
        "/admin/simulators",
        json={
            "slug": "whatsapp",
            "title": "Otro WhatsApp",
            "module_type": "simulator",
            "content_area": "comunicacion",
        },
        headers=admin_token_headers(admin),
    )

    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_admin_update_simulator_deactivate(client, db_session):
    ac, _ = client
    admin = await create_test_admin(db_session)
    sim = await create_test_simulator(db_session, slug="whatsapp")

    resp = await ac.patch(
        f"/admin/simulators/{sim.id}",
        json={"is_active": False},
        headers=admin_token_headers(admin),
    )

    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


@pytest.mark.asyncio
async def test_admin_list_requests_filter_by_status(client, db_session):
    ac, _ = client
    admin = await create_test_admin(db_session)
    user = await create_test_user(db_session)

    from app.models.community import LearningRequest, RequestStatus
    req1 = LearningRequest(user_id=user.id, description="Aprender correo", status=RequestStatus.received)
    req2 = LearningRequest(user_id=user.id, description="Aprender fotos", status=RequestStatus.available)
    db_session.add_all([req1, req2])
    await db_session.commit()

    resp = await ac.get(
        "/admin/requests?status=received",
        headers=admin_token_headers(admin),
    )

    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["status"] == "received"


@pytest.mark.asyncio
async def test_user_token_cannot_access_admin(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    resp = await ac.get("/admin/stats", headers=auth_headers(user))

    # El token de usuario no tiene rol admin — el backend lo rechaza con 401
    assert resp.status_code == 401
