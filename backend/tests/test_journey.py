"""Tests del arco de usuario: estado del recorrido y graduación."""
import pytest

from tests.conftest import create_test_user, create_test_achievement, create_test_lesson, auth_headers


async def _earn_all_achievements(db_session, user, count: int = 10):
    """Crea `count` logros y los asigna al usuario."""
    from app.models.achievement import Achievement, UserAchievement, TriggerType

    achievements = []
    for i in range(count):
        ach = await create_test_achievement(
            db_session,
            key=f"auto_{i}",
            trigger_type=TriggerType.lesson_count,
            threshold=1,
        )
        ua = UserAchievement(user_id=user.id, achievement_id=ach.id)
        db_session.add(ua)
        achievements.append(ach)

    await db_session.commit()
    return achievements


@pytest.mark.asyncio
async def test_get_journey_status_returns_stage(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    resp = await ac.get("/users/me/journey", headers=auth_headers(user))

    assert resp.status_code == 200
    data = resp.json()
    assert data["stage"] == "onboarding"
    assert "areas_progress" in data
    assert data["achievements_earned"] == 0
    assert data["achievements_total"] == 0
    assert data["achievement_pct"] == 0
    assert data["ready_to_graduate"] is False
    assert data["pending_voted_requests"] == 0


@pytest.mark.asyncio
async def test_journey_counts_earned_achievements(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    await _earn_all_achievements(db_session, user, count=3)

    # 3 earned out of 3 total → 100%
    resp = await ac.get("/users/me/journey", headers=auth_headers(user))
    data = resp.json()

    assert data["achievements_earned"] == 3
    assert data["achievements_total"] == 3
    assert data["achievement_pct"] == 100


@pytest.mark.asyncio
async def test_ready_to_graduate_false_below_threshold(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    # 8 earned, 10 total → 80% < 85%
    from app.models.achievement import Achievement, UserAchievement, TriggerType
    all_achs = []
    for i in range(10):
        ach = await create_test_achievement(
            db_session, key=f"ach_{i}", trigger_type=TriggerType.lesson_count, threshold=1
        )
        all_achs.append(ach)
    await db_session.commit()

    for ach in all_achs[:8]:
        db_session.add(UserAchievement(user_id=user.id, achievement_id=ach.id))
    await db_session.commit()

    resp = await ac.get("/users/me/journey", headers=auth_headers(user))
    data = resp.json()

    assert data["achievement_pct"] == 80
    assert data["ready_to_graduate"] is False


@pytest.mark.asyncio
async def test_ready_to_graduate_true_at_threshold(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    # 17 earned, 20 total → 85% exactly
    from app.models.achievement import Achievement, UserAchievement, TriggerType
    all_achs = []
    for i in range(20):
        ach = await create_test_achievement(
            db_session, key=f"g_{i}", trigger_type=TriggerType.lesson_count, threshold=1
        )
        all_achs.append(ach)
    await db_session.commit()

    for ach in all_achs[:17]:
        db_session.add(UserAchievement(user_id=user.id, achievement_id=ach.id))
    await db_session.commit()

    resp = await ac.get("/users/me/journey", headers=auth_headers(user))
    data = resp.json()

    assert data["achievement_pct"] == 85
    assert data["ready_to_graduate"] is True


@pytest.mark.asyncio
async def test_graduate_fails_below_threshold(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    # 0 achievements → 0% < 85%
    resp = await ac.post("/users/me/graduate", headers=auth_headers(user))

    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_graduate_succeeds_at_threshold(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    # 100% achievements → above threshold
    await _earn_all_achievements(db_session, user, count=5)

    resp = await ac.post("/users/me/graduate", headers=auth_headers(user))

    assert resp.status_code == 200
    data = resp.json()
    assert "summary_id" in data
    assert "file_url" in data
    assert data["achievement_pct"] == 100


@pytest.mark.asyncio
async def test_graduate_marks_user_as_graduated(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    await _earn_all_achievements(db_session, user, count=5)

    await ac.post("/users/me/graduate", headers=auth_headers(user))

    journey_resp = await ac.get("/users/me/journey", headers=auth_headers(user))
    assert journey_resp.json()["stage"] == "graduated"


@pytest.mark.asyncio
async def test_graduate_twice_returns_409(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    await _earn_all_achievements(db_session, user, count=5)

    await ac.post("/users/me/graduate", headers=auth_headers(user))
    resp = await ac.post("/users/me/graduate", headers=auth_headers(user))

    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_get_summaries_empty(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    resp = await ac.get("/users/me/summaries", headers=auth_headers(user))

    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_pending_voted_requests_counted(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    from app.models.community import LearningRequest, RequestVote, RequestStatus
    req = LearningRequest(user_id=user.id, description="Cómo usar WhatsApp", status=RequestStatus.in_development)
    db_session.add(req)
    await db_session.commit()
    await db_session.refresh(req)

    vote = RequestVote(request_id=req.id, user_id=user.id)
    db_session.add(vote)
    await db_session.commit()

    resp = await ac.get("/users/me/journey", headers=auth_headers(user))
    assert resp.json()["pending_voted_requests"] == 1


@pytest.mark.asyncio
async def test_pending_voted_requests_excludes_available(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)

    from app.models.community import LearningRequest, RequestVote, RequestStatus
    req = LearningRequest(user_id=user.id, description="Cómo usar WhatsApp", status=RequestStatus.available)
    db_session.add(req)
    await db_session.commit()
    await db_session.refresh(req)

    vote = RequestVote(request_id=req.id, user_id=user.id)
    db_session.add(vote)
    await db_session.commit()

    resp = await ac.get("/users/me/journey", headers=auth_headers(user))
    assert resp.json()["pending_voted_requests"] == 0


@pytest.mark.asyncio
async def test_get_summaries_after_graduation(client, db_session):
    ac, _ = client
    user = await create_test_user(db_session)
    await _earn_all_achievements(db_session, user, count=5)

    await ac.post("/users/me/graduate", headers=auth_headers(user))

    resp = await ac.get("/users/me/summaries", headers=auth_headers(user))
    summaries = resp.json()

    assert len(summaries) == 1
    assert summaries[0]["summary_type"] == "graduation"
    assert summaries[0]["title"] == "Mi recorrido en TecnoAmigo"
