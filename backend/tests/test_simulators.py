"""Tests de sesiones de simuladores."""
import pytest

from tests.conftest import create_test_user, create_test_simulator, auth_headers


@pytest.mark.asyncio
async def test_catalog_returns_active_simulators(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    await create_test_simulator(db_session, slug="whatsapp", title="WhatsApp")
    await create_test_simulator(db_session, slug="bancoestado", title="BancoEstado")

    resp = await ac.get("/simulators", headers=auth_headers(user))

    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_inactive_simulator_not_in_catalog(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    from app.models.content import SimulatorCatalog, ContentArea, ModuleType
    sim = SimulatorCatalog(slug="beta", title="Beta", content_area=ContentArea.gobierno,
                           module_type=ModuleType.simulator, is_active=False)
    db_session.add(sim)
    await db_session.commit()

    resp = await ac.get("/simulators", headers=auth_headers(user))
    slugs = [s["slug"] for s in resp.json()]
    assert "beta" not in slugs


@pytest.mark.asyncio
async def test_start_session(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    await create_test_simulator(db_session, slug="whatsapp")

    resp = await ac.post(
        "/simulators/sessions",
        json={"simulator_slug": "whatsapp"},
        headers=auth_headers(user),
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["completed"] is False
    assert data["steps_completed"] == 0


@pytest.mark.asyncio
async def test_start_session_unknown_slug_returns_404(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    resp = await ac.post(
        "/simulators/sessions",
        json={"simulator_slug": "inexistente"},
        headers=auth_headers(user),
    )

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_session_steps(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    await create_test_simulator(db_session, slug="whatsapp")

    start = await ac.post(
        "/simulators/sessions",
        json={"simulator_slug": "whatsapp"},
        headers=auth_headers(user),
    )
    session_id = start.json()["id"]

    resp = await ac.patch(
        f"/simulators/sessions/{session_id}",
        json={"steps_completed": 3},
        headers=auth_headers(user),
    )

    assert resp.status_code == 200
    assert resp.json()["steps_completed"] == 3


@pytest.mark.asyncio
async def test_complete_session(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    await create_test_simulator(db_session, slug="whatsapp")

    start = await ac.post(
        "/simulators/sessions",
        json={"simulator_slug": "whatsapp"},
        headers=auth_headers(user),
    )
    session_id = start.json()["id"]

    resp = await ac.post(
        f"/simulators/sessions/{session_id}/complete",
        headers=auth_headers(user),
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["completed"] is True
    assert data["ended_at"] is not None


@pytest.mark.asyncio
async def test_complete_session_registers_activity(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    await create_test_simulator(db_session, slug="whatsapp")

    start = await ac.post(
        "/simulators/sessions",
        json={"simulator_slug": "whatsapp"},
        headers=auth_headers(user),
    )
    session_id = start.json()["id"]
    await ac.post(f"/simulators/sessions/{session_id}/complete", headers=auth_headers(user))

    from sqlalchemy import select
    from app.models.progress import UserActivity
    result = await db_session.execute(select(UserActivity).where(UserActivity.user_id == user.id))
    activity = result.scalar_one_or_none()

    assert activity is not None
    assert activity.total_active_days == 1


@pytest.mark.asyncio
async def test_complete_already_completed_returns_404(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    await create_test_simulator(db_session, slug="whatsapp")

    start = await ac.post(
        "/simulators/sessions",
        json={"simulator_slug": "whatsapp"},
        headers=auth_headers(user),
    )
    session_id = start.json()["id"]
    await ac.post(f"/simulators/sessions/{session_id}/complete", headers=auth_headers(user))

    resp = await ac.post(
        f"/simulators/sessions/{session_id}/complete",
        headers=auth_headers(user),
    )
    assert resp.status_code == 404
