"""Tests de la evaluación inicial y generación del competency_map."""
import pytest

from tests.conftest import create_test_user, create_test_lesson, auth_headers
from app.models.content import ContentArea, ModuleType


FULL_ASSESSMENT = [
    {"question_key": "whatsapp_mensajes",    "answer_value": 0},
    {"question_key": "whatsapp_fotos",       "answer_value": 0},
    {"question_key": "videollamada",         "answer_value": 0},
    {"question_key": "banca_consulta",       "answer_value": 2},
    {"question_key": "banca_transferencia",  "answer_value": 2},
    {"question_key": "clave_unica",          "answer_value": 1},
    {"question_key": "tramites_web",         "answer_value": 0},
    {"question_key": "guardar_archivos",     "answer_value": 0},
    {"question_key": "abrir_pdf",            "answer_value": 1},
    {"question_key": "reconocer_estafa",     "answer_value": 0},
    {"question_key": "llamadas_sospechosas", "answer_value": 0},
]


@pytest.mark.asyncio
async def test_get_questions_returns_all(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    resp = await ac.get("/assessment/questions", headers=auth_headers(user))

    assert resp.status_code == 200
    keys = [q["key"] for q in resp.json()]
    assert "whatsapp_mensajes" in keys
    assert "banca_consulta" in keys


@pytest.mark.asyncio
async def test_submit_assessment_returns_competency_map(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    resp = await ac.post(
        "/assessment",
        json={"answers": FULL_ASSESSMENT},
        headers=auth_headers(user),
    )

    assert resp.status_code == 200
    data = resp.json()
    assert "competency_map" in data
    # Banca debe ser 1.0 (todas respuestas = 2)
    assert data["competency_map"]["banca"] == 1.0
    # Comunicación debe ser 0.0 (todas respuestas = 0)
    assert data["competency_map"]["comunicacion"] == 0.0


@pytest.mark.asyncio
async def test_submit_assessment_advances_journey_stage(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    resp = await ac.post(
        "/assessment",
        json={"answers": FULL_ASSESSMENT},
        headers=auth_headers(user),
    )

    assert resp.json()["journey_stage"] == "learning"


@pytest.mark.asyncio
async def test_submit_assessment_recommends_weak_areas(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    # Crear lección de comunicación para que pueda recomendarse
    await create_test_lesson(
        db_session,
        title="WhatsApp paso a paso",
        content_area=ContentArea.comunicacion,
    )

    resp = await ac.post(
        "/assessment",
        json={"answers": FULL_ASSESSMENT},
        headers=auth_headers(user),
    )

    recs = resp.json()["recommended_lessons"]
    areas = [r["content_area"] for r in recs]
    # Comunicación tiene score 0 → debe recomendarse
    assert "comunicacion" in areas
    # Banca tiene score 1.0 → no debe recomendarse
    assert "banca" not in areas


@pytest.mark.asyncio
async def test_submit_assessment_invalid_key_returns_400(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    resp = await ac.post(
        "/assessment",
        json={"answers": [{"question_key": "clave_inexistente", "answer_value": 1}]},
        headers=auth_headers(user),
    )

    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_submit_assessment_invalid_answer_value_returns_422(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    resp = await ac.post(
        "/assessment",
        json={"answers": [{"question_key": "whatsapp_mensajes", "answer_value": 5}]},
        headers=auth_headers(user),
    )

    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_resubmit_assessment_replaces_previous(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    await ac.post("/assessment", json={"answers": FULL_ASSESSMENT}, headers=auth_headers(user))

    # Segunda evaluación con respuestas distintas
    new_answers = [{"question_key": "whatsapp_mensajes", "answer_value": 2}]
    resp = await ac.post(
        "/assessment",
        json={"answers": new_answers},
        headers=auth_headers(user),
    )

    assert resp.status_code == 200
    # Solo un área en el mapa esta vez
    assert len(resp.json()["competency_map"]) == 1
