"""Tests de los endpoints de autenticación."""
import pytest
from httpx import AsyncClient

from tests.conftest import MockSmsService

PHONE = "+56912345678"
BAD_PHONE = "12345"


# ---------------------------------------------------------------------------
# POST /auth/send-sms
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_send_sms_returns_204(client):
    ac, sms = client
    resp = await ac.post("/auth/send-sms", json={"phone_number": PHONE})
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_send_sms_delivers_code(client):
    ac, sms = client
    await ac.post("/auth/send-sms", json={"phone_number": PHONE})
    assert sms.last_code_for(PHONE) is not None
    assert len(sms.last_code_for(PHONE)) == 6


@pytest.mark.asyncio
async def test_send_sms_invalid_phone_returns_422(client):
    ac, _ = client
    resp = await ac.post("/auth/send-sms", json={"phone_number": BAD_PHONE})
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /auth/verify-sms
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_verify_sms_new_user_returns_tokens(client):
    ac, sms = client
    await ac.post("/auth/send-sms", json={"phone_number": PHONE})
    code = sms.last_code_for(PHONE)

    resp = await ac.post("/auth/verify-sms", json={"phone_number": PHONE, "code": code})

    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["is_new_user"] is True


@pytest.mark.asyncio
async def test_verify_sms_existing_user_is_new_false(client):
    ac, sms = client
    # Primera vez — crea el usuario
    await ac.post("/auth/send-sms", json={"phone_number": PHONE})
    code = sms.last_code_for(PHONE)
    await ac.post("/auth/verify-sms", json={"phone_number": PHONE, "code": code})

    # Segunda vez — usuario ya existe
    await ac.post("/auth/send-sms", json={"phone_number": PHONE})
    code2 = sms.last_code_for(PHONE)
    resp = await ac.post("/auth/verify-sms", json={"phone_number": PHONE, "code": code2})

    assert resp.status_code == 200
    assert resp.json()["is_new_user"] is False


@pytest.mark.asyncio
async def test_verify_sms_wrong_code_returns_400(client):
    ac, sms = client
    await ac.post("/auth/send-sms", json={"phone_number": PHONE})

    resp = await ac.post("/auth/verify-sms", json={"phone_number": PHONE, "code": "000000"})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_verify_sms_used_code_returns_400(client):
    ac, sms = client
    await ac.post("/auth/send-sms", json={"phone_number": PHONE})
    code = sms.last_code_for(PHONE)

    # Primer uso — válido
    await ac.post("/auth/verify-sms", json={"phone_number": PHONE, "code": code})

    # Segundo uso del mismo código — inválido
    resp = await ac.post("/auth/verify-sms", json={"phone_number": PHONE, "code": code})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_verify_sms_code_format_422(client):
    ac, _ = client
    resp = await ac.post("/auth/verify-sms", json={"phone_number": PHONE, "code": "abc"})
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /auth/refresh
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_refresh_returns_new_access_token(client):
    ac, sms = client
    await ac.post("/auth/send-sms", json={"phone_number": PHONE})
    code = sms.last_code_for(PHONE)
    login = await ac.post("/auth/verify-sms", json={"phone_number": PHONE, "code": code})
    refresh_token = login.json()["refresh_token"]

    resp = await ac.post("/auth/refresh", json={"refresh_token": refresh_token})

    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_refresh_with_garbage_token_returns_401(client):
    ac, _ = client
    resp = await ac.post("/auth/refresh", json={"refresh_token": "token.falso.aqui"})
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# POST /auth/logout
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_logout_revokes_refresh_token(client):
    ac, sms = client
    await ac.post("/auth/send-sms", json={"phone_number": PHONE})
    code = sms.last_code_for(PHONE)
    login = await ac.post("/auth/verify-sms", json={"phone_number": PHONE, "code": code})
    tokens = login.json()

    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    await ac.post("/auth/logout", json={"refresh_token": tokens["refresh_token"]}, headers=headers)

    # Intentar usar el refresh token revocado debe fallar
    resp = await ac.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_logout_requires_authentication(client):
    ac, _ = client
    resp = await ac.post("/auth/logout", json={"refresh_token": "cualquiera"})
    assert resp.status_code == 401
