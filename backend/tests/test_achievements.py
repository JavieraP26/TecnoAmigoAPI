"""Tests de logros: desbloqueo tras completar lecciones y evaluación."""
import pytest

from tests.conftest import (
    create_test_user, create_test_lesson, create_test_achievement, auth_headers
)
from app.models.achievement import TriggerType
from app.models.content import ContentArea


@pytest.mark.asyncio
async def test_no_achievements_earned_on_start(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    await create_test_achievement(db_session, key="primera_leccion")

    resp = await ac.get("/achievements/me", headers=auth_headers(user))

    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_lesson_count_achievement_unlocked(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    lesson = await create_test_lesson(db_session)
    await create_test_achievement(
        db_session, key="primera_leccion",
        trigger_type=TriggerType.lesson_count, threshold=1,
    )

    await ac.post(f"/progress/{lesson.id}/start", headers=auth_headers(user))
    resp = await ac.post(f"/progress/{lesson.id}/complete", headers=auth_headers(user))

    assert resp.status_code == 200
    assert "primera_leccion" in resp.json()["newly_earned_achievements"]


@pytest.mark.asyncio
async def test_lesson_count_not_unlocked_before_threshold(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    lesson = await create_test_lesson(db_session)
    await create_test_achievement(
        db_session, key="cinco_lecciones",
        trigger_type=TriggerType.lesson_count, threshold=5,
    )

    await ac.post(f"/progress/{lesson.id}/start", headers=auth_headers(user))
    resp = await ac.post(f"/progress/{lesson.id}/complete", headers=auth_headers(user))

    assert "cinco_lecciones" not in resp.json()["newly_earned_achievements"]


@pytest.mark.asyncio
async def test_area_first_achievement_unlocked(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    lesson = await create_test_lesson(db_session, content_area=ContentArea.banca)
    await create_test_achievement(
        db_session, key="banca_primer_paso",
        trigger_type=TriggerType.area_first,
        content_area=ContentArea.banca.value,
    )

    await ac.post(f"/progress/{lesson.id}/start", headers=auth_headers(user))
    resp = await ac.post(f"/progress/{lesson.id}/complete", headers=auth_headers(user))

    assert "banca_primer_paso" in resp.json()["newly_earned_achievements"]


@pytest.mark.asyncio
async def test_area_complete_achievement_unlocked(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    lesson = await create_test_lesson(db_session, content_area=ContentArea.seguridad)
    await create_test_achievement(
        db_session, key="seguridad_completa",
        trigger_type=TriggerType.area_complete,
        content_area=ContentArea.seguridad.value,
    )

    await ac.post(f"/progress/{lesson.id}/start", headers=auth_headers(user))
    resp = await ac.post(f"/progress/{lesson.id}/complete", headers=auth_headers(user))

    # Solo hay 1 lección en seguridad y ya la completó → área completa
    assert "seguridad_completa" in resp.json()["newly_earned_achievements"]


@pytest.mark.asyncio
async def test_area_complete_not_unlocked_if_more_lessons_pending(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    lesson1 = await create_test_lesson(db_session, title="Seg 1", content_area=ContentArea.seguridad)
    await create_test_lesson(db_session, title="Seg 2", content_area=ContentArea.seguridad)
    await create_test_achievement(
        db_session, key="seguridad_completa",
        trigger_type=TriggerType.area_complete,
        content_area=ContentArea.seguridad.value,
    )

    await ac.post(f"/progress/{lesson1.id}/start", headers=auth_headers(user))
    resp = await ac.post(f"/progress/{lesson1.id}/complete", headers=auth_headers(user))

    assert "seguridad_completa" not in resp.json()["newly_earned_achievements"]


@pytest.mark.asyncio
async def test_assessment_achievement_unlocked(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    await create_test_achievement(
        db_session, key="evaluacion_completada",
        trigger_type=TriggerType.assessment_complete,
    )

    resp = await ac.post(
        "/assessment",
        json={"answers": [{"question_key": "whatsapp_mensajes", "answer_value": 1}]},
        headers=auth_headers(user),
    )

    assert resp.status_code == 200
    # El logro se gana pero no se devuelve en assessment (se consulta por /achievements/me)
    earned = await ac.get("/achievements/me", headers=auth_headers(user))
    keys = [a["key"] for a in earned.json()]
    assert "evaluacion_completada" in keys


@pytest.mark.asyncio
async def test_achievement_not_duplicated(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    lesson = await create_test_lesson(db_session)
    await create_test_achievement(
        db_session, key="primera_leccion",
        trigger_type=TriggerType.lesson_count, threshold=1,
    )

    await ac.post(f"/progress/{lesson.id}/start", headers=auth_headers(user))
    await ac.post(f"/progress/{lesson.id}/complete", headers=auth_headers(user))

    earned = await ac.get("/achievements/me", headers=auth_headers(user))
    # Solo debe aparecer una vez
    keys = [a["key"] for a in earned.json()]
    assert keys.count("primera_leccion") == 1


@pytest.mark.asyncio
async def test_catalog_shows_all_with_earned_flag(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    lesson = await create_test_lesson(db_session)
    await create_test_achievement(db_session, key="ganado", trigger_type=TriggerType.lesson_count, threshold=1)
    await create_test_achievement(db_session, key="pendiente", trigger_type=TriggerType.lesson_count, threshold=99)

    await ac.post(f"/progress/{lesson.id}/start", headers=auth_headers(user))
    await ac.post(f"/progress/{lesson.id}/complete", headers=auth_headers(user))

    resp = await ac.get("/achievements", headers=auth_headers(user))
    data = {a["key"]: a["earned"] for a in resp.json()}

    assert data["ganado"] is True
    assert data["pendiente"] is False
