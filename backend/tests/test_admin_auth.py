"""Tests de autenticación de administrador (login + MFA TOTP)."""
import pyotp
import pytest

from tests.conftest import create_test_admin


@pytest.mark.asyncio
async def test_admin_login_returns_pre_auth_token(client, db_session):
    ac, _ = client
    await create_test_admin(db_session, email="admin@test.com", password="TestPass1234!")

    resp = await ac.post(
        "/admin/auth/login",
        json={"email": "admin@test.com", "password": "TestPass1234!"},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert "pre_auth_token" in data


@pytest.mark.asyncio
async def test_admin_first_login_returns_totp_setup_uri(client, db_session):
    ac, _ = client
    await create_test_admin(db_session, email="admin@test.com", password="TestPass1234!")

    resp = await ac.post(
        "/admin/auth/login",
        json={"email": "admin@test.com", "password": "TestPass1234!"},
    )

    data = resp.json()
    assert data["totp_setup_uri"] is not None
    assert "otpauth://" in data["totp_setup_uri"]


@pytest.mark.asyncio
async def test_admin_login_wrong_password_returns_401(client, db_session):
    ac, _ = client
    await create_test_admin(db_session, email="admin@test.com", password="TestPass1234!")

    resp = await ac.post(
        "/admin/auth/login",
        json={"email": "admin@test.com", "password": "incorrecta"},
    )

    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_admin_login_unknown_email_returns_401(client, db_session):
    ac, _ = client

    resp = await ac.post(
        "/admin/auth/login",
        json={"email": "noexiste@test.com", "password": "cualquiera"},
    )

    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_admin_verify_mfa_with_valid_totp(client, db_session):
    ac, _ = client
    await create_test_admin(db_session, email="admin@test.com", password="TestPass1234!")

    # Paso 1: login
    login_resp = await ac.post(
        "/admin/auth/login",
        json={"email": "admin@test.com", "password": "TestPass1234!"},
    )
    pre_auth_token = login_resp.json()["pre_auth_token"]
    totp_uri = login_resp.json()["totp_setup_uri"]

    # Extraer el secret del URI para generar un código válido
    secret = pyotp.parse_uri(totp_uri).secret
    totp_code = pyotp.TOTP(secret).now()

    # Paso 2: verificar MFA
    resp = await ac.post(
        "/admin/auth/verify-mfa",
        json={"pre_auth_token": pre_auth_token, "totp_code": totp_code},
    )

    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_admin_verify_mfa_wrong_code_returns_401(client, db_session):
    ac, _ = client
    await create_test_admin(db_session, email="admin@test.com", password="TestPass1234!")

    login_resp = await ac.post(
        "/admin/auth/login",
        json={"email": "admin@test.com", "password": "TestPass1234!"},
    )
    pre_auth_token = login_resp.json()["pre_auth_token"]

    resp = await ac.post(
        "/admin/auth/verify-mfa",
        json={"pre_auth_token": pre_auth_token, "totp_code": "000000"},
    )

    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_admin_verify_mfa_invalid_pre_auth_token_returns_401(client, db_session):
    ac, _ = client

    resp = await ac.post(
        "/admin/auth/verify-mfa",
        json={"pre_auth_token": "token.invalido.xxx", "totp_code": "123456"},
    )

    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_admin_second_login_no_setup_uri(client, db_session):
    ac, _ = client
    await create_test_admin(db_session, email="admin@test.com", password="TestPass1234!")

    # Primer login → obtener secret y completar MFA
    login_resp = await ac.post(
        "/admin/auth/login",
        json={"email": "admin@test.com", "password": "TestPass1234!"},
    )
    pre_auth_token = login_resp.json()["pre_auth_token"]
    totp_uri = login_resp.json()["totp_setup_uri"]
    secret = pyotp.parse_uri(totp_uri).secret
    totp_code = pyotp.TOTP(secret).now()
    await ac.post(
        "/admin/auth/verify-mfa",
        json={"pre_auth_token": pre_auth_token, "totp_code": totp_code},
    )

    # Segundo login → no debe devolver URI de setup
    second_resp = await ac.post(
        "/admin/auth/login",
        json={"email": "admin@test.com", "password": "TestPass1234!"},
    )

    assert second_resp.status_code == 200
    assert second_resp.json()["totp_setup_uri"] is None
