"""Tests de perfil de usuario."""
import pytest

from tests.conftest import create_test_user, auth_headers


@pytest.mark.asyncio
async def test_get_profile(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    resp = await ac.get("/users/me", headers=auth_headers(user))

    assert resp.status_code == 200
    data = resp.json()
    assert data["phone_number"] == user.phone_number
    assert data["journey_stage"] == "onboarding"


@pytest.mark.asyncio
async def test_update_profile_name_and_city(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    resp = await ac.patch(
        "/users/me",
        json={"full_name": "María González", "city": "Valparaíso", "age": 68},
        headers=auth_headers(user),
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["full_name"] == "María González"
    assert data["city"] == "Valparaíso"
    assert data["age"] == 68


@pytest.mark.asyncio
async def test_update_profile_partial(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    await ac.patch("/users/me", json={"full_name": "Rosa"}, headers=auth_headers(user))
    resp = await ac.patch("/users/me", json={"city": "Santiago"}, headers=auth_headers(user))

    data = resp.json()
    assert data["full_name"] == "Rosa"
    assert data["city"] == "Santiago"


@pytest.mark.asyncio
async def test_update_invalid_duration_returns_422(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    resp = await ac.patch(
        "/users/me",
        json={"preferred_lesson_duration": 7},
        headers=auth_headers(user),
    )

    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_update_invalid_age_returns_422(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    resp = await ac.patch("/users/me", json={"age": 5}, headers=auth_headers(user))

    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_profile_requires_auth(client, db_session):
    ac, _ = client

    resp = await ac.get("/users/me")

    assert resp.status_code == 401
