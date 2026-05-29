"""Tests de peticiones de aprendizaje."""
import pytest

from tests.conftest import create_test_user, auth_headers


@pytest.mark.asyncio
async def test_create_request(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    resp = await ac.post(
        "/requests",
        json={"description": "Quiero aprender a pagar cuentas por internet"},
        headers=auth_headers(user),
    )

    assert resp.status_code == 201
    data = resp.json()
    assert data["request"]["votes"] == 1
    assert data["request"]["is_mine"] is True
    assert data["similar_found"] is None


@pytest.mark.asyncio
async def test_create_request_detects_similar_with_percentage(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    await ac.post(
        "/requests",
        json={"description": "Quiero aprender a pagar cuentas por internet banco"},
        headers=auth_headers(user),
    )

    user2 = await create_test_user(db_session, phone="+56987654321")
    resp = await ac.post(
        "/requests",
        json={"description": "Como pagar cuentas usando internet banco"},
        headers=auth_headers(user2),
    )

    assert resp.status_code == 201
    similar = resp.json()["similar_found"]
    assert similar is not None
    assert 0 < similar["similarity_pct"] <= 100


@pytest.mark.asyncio
async def test_create_request_high_similarity_above_threshold(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    await ac.post(
        "/requests",
        json={"description": "Quiero aprender abrir archivos PDF teléfono celular"},
        headers=auth_headers(user),
    )

    user2 = await create_test_user(db_session, phone="+56987654321")
    resp = await ac.post(
        "/requests",
        json={"description": "Cómo abrir archivos PDF desde teléfono celular"},
        headers=auth_headers(user2),
    )

    similar = resp.json()["similar_found"]
    assert similar is not None
    assert similar["similarity_pct"] >= 25


@pytest.mark.asyncio
async def test_create_request_no_similar_when_different_topic(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    await ac.post(
        "/requests",
        json={"description": "Quiero aprender videollamadas familia WhatsApp"},
        headers=auth_headers(user),
    )

    user2 = await create_test_user(db_session, phone="+56987654321")
    resp = await ac.post(
        "/requests",
        json={"description": "Cómo reconocer llamadas estafa sospechosas"},
        headers=auth_headers(user2),
    )

    assert resp.json()["similar_found"] is None


@pytest.mark.asyncio
async def test_create_request_too_short_returns_422(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    resp = await ac.post(
        "/requests",
        json={"description": "Pagar"},
        headers=auth_headers(user),
    )

    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_requests_ordered_by_votes(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    user2 = await create_test_user(db_session, phone="+56987654321")

    await ac.post(
        "/requests",
        json={"description": "Aprender usar WhatsApp hablar familia amigos"},
        headers=auth_headers(user),
    )
    r2 = await ac.post(
        "/requests",
        json={"description": "Cómo abrir documentos PDF teléfono celular"},
        headers=auth_headers(user2),
    )
    r2_id = r2.json()["request"]["id"]
    await ac.post(f"/requests/{r2_id}/vote", headers=auth_headers(user))

    resp = await ac.get("/requests", headers=auth_headers(user))
    data = resp.json()

    assert data[0]["votes"] >= data[1]["votes"]


@pytest.mark.asyncio
async def test_vote_request(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    user2 = await create_test_user(db_session, phone="+56987654321")

    r = await ac.post(
        "/requests",
        json={"description": "Aprender hacer videollamadas familia celular"},
        headers=auth_headers(user),
    )
    request_id = r.json()["request"]["id"]

    resp = await ac.post(f"/requests/{request_id}/vote", headers=auth_headers(user2))

    assert resp.status_code == 200
    assert resp.json()["votes"] == 2
    assert resp.json()["already_voted"] is True


@pytest.mark.asyncio
async def test_vote_twice_returns_409(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    r = await ac.post(
        "/requests",
        json={"description": "Cómo reconocer llamadas estafa teléfono celular"},
        headers=auth_headers(user),
    )
    request_id = r.json()["request"]["id"]

    resp = await ac.post(f"/requests/{request_id}/vote", headers=auth_headers(user))

    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_vote_nonexistent_request_returns_404(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    import uuid

    resp = await ac.post(f"/requests/{uuid.uuid4()}/vote", headers=auth_headers(user))

    assert resp.status_code == 404
