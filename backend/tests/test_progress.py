"""Tests de progreso y actividad del usuario."""
import pytest
from datetime import date, timedelta

from tests.conftest import create_test_user, create_test_lesson, auth_headers


@pytest.mark.asyncio
async def test_start_lesson_creates_progress(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    lesson = await create_test_lesson(db_session)

    resp = await ac.post(f"/progress/{lesson.id}/start", headers=auth_headers(user))

    assert resp.status_code == 201
    data = resp.json()
    assert data["completion_pct"] == 0
    assert data["completed"] is False


@pytest.mark.asyncio
async def test_start_lesson_twice_is_idempotent(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    lesson = await create_test_lesson(db_session)

    await ac.post(f"/progress/{lesson.id}/start", headers=auth_headers(user))
    resp = await ac.post(f"/progress/{lesson.id}/start", headers=auth_headers(user))

    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_update_progress(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    lesson = await create_test_lesson(db_session)

    await ac.post(f"/progress/{lesson.id}/start", headers=auth_headers(user))
    resp = await ac.patch(
        f"/progress/{lesson.id}",
        json={"completion_pct": 75},
        headers=auth_headers(user),
    )

    assert resp.status_code == 200
    assert resp.json()["completion_pct"] == 75


@pytest.mark.asyncio
async def test_update_progress_without_start_returns_404(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    lesson = await create_test_lesson(db_session)

    resp = await ac.patch(
        f"/progress/{lesson.id}",
        json={"completion_pct": 50},
        headers=auth_headers(user),
    )

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_complete_lesson_marks_done(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    lesson = await create_test_lesson(db_session)

    await ac.post(f"/progress/{lesson.id}/start", headers=auth_headers(user))
    resp = await ac.post(f"/progress/{lesson.id}/complete", headers=auth_headers(user))

    assert resp.status_code == 200
    data = resp.json()
    assert data["completed"] is True
    assert data["completion_pct"] == 100
    assert data["completed_at"] is not None


@pytest.mark.asyncio
async def test_complete_lesson_unlocks_next(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    first = await create_test_lesson(db_session, title="Primera")
    second = await create_test_lesson(db_session, title="Segunda", prerequisite_id=first.id)

    await ac.post(f"/progress/{first.id}/start", headers=auth_headers(user))
    await ac.post(f"/progress/{first.id}/complete", headers=auth_headers(user))

    resp = await ac.get(f"/lessons/{second.id}", headers=auth_headers(user))
    assert resp.json()["is_available"] is True


@pytest.mark.asyncio
async def test_complete_lesson_registers_activity(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    lesson = await create_test_lesson(db_session)

    await ac.post(f"/progress/{lesson.id}/start", headers=auth_headers(user))
    await ac.post(f"/progress/{lesson.id}/complete", headers=auth_headers(user))

    from sqlalchemy import select
    from app.models.progress import UserActivity
    result = await db_session.execute(select(UserActivity).where(UserActivity.user_id == user.id))
    activity = result.scalar_one_or_none()

    assert activity is not None
    assert activity.total_active_days == 1
    assert activity.last_visit_date == date.today()


@pytest.mark.asyncio
async def test_completion_pct_out_of_range_returns_422(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    lesson = await create_test_lesson(db_session)

    await ac.post(f"/progress/{lesson.id}/start", headers=auth_headers(user))
    resp = await ac.patch(
        f"/progress/{lesson.id}",
        json={"completion_pct": 150},
        headers=auth_headers(user),
    )

    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Contexto de bienvenida — sin racha, sin presión
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_welcome_context_new_user(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    resp = await ac.get("/progress/welcome", headers=auth_headers(user))

    assert resp.status_code == 200
    data = resp.json()
    assert data["returning"] is False
    assert data["total_active_days"] == 0


@pytest.mark.asyncio
async def test_welcome_context_after_activity(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    lesson = await create_test_lesson(db_session)

    await ac.post(f"/progress/{lesson.id}/start", headers=auth_headers(user))
    await ac.post(f"/progress/{lesson.id}/complete", headers=auth_headers(user))

    resp = await ac.get("/progress/welcome", headers=auth_headers(user))

    data = resp.json()
    # Mismo día → no se considera "regresando"
    assert data["returning"] is False
    assert data["total_active_days"] == 1


@pytest.mark.asyncio
async def test_welcome_context_returning_after_days(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    from app.models.progress import UserActivity
    from datetime import datetime, timezone

    # Simula que el usuario tuvo actividad hace 3 días
    past_date = date.today() - timedelta(days=3)
    activity = UserActivity(
        user_id=user.id,
        first_visit_date=past_date,
        last_visit_date=past_date,
        total_active_days=5,
    )
    db_session.add(activity)
    await db_session.commit()

    resp = await ac.get("/progress/welcome", headers=auth_headers(user))

    data = resp.json()
    assert data["returning"] is True
    assert data["days_since_last_visit"] == 3
    assert data["total_active_days"] == 5
