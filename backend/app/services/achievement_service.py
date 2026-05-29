"""
Evaluación y desbloqueo de logros.

Regla de diseño: este service no sabe nada de HTTP ni de routers.
Es llamado por progress_service y assessment_service tras eventos de negocio.
Devuelve los keys de logros recién ganados para que el caller los exponga al frontend.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.achievement import Achievement, UserAchievement, TriggerType
from app.models.progress import UserProgress
from app.models.content import Lesson, ContentArea
from app.core.logging_config import get_logger

logger = get_logger(__name__)


async def evaluate_after_lesson(
    db: AsyncSession,
    user_id: uuid.UUID,
    completed_lesson: Lesson,
) -> list[str]:
    """
    Evalúa qué logros se desbloquean tras completar una lección.
    Devuelve la lista de keys recién ganados (puede ser vacía).
    """
    all_achievements = await _get_all_achievements(db)
    already_earned_ids = await _get_earned_ids(db, user_id)
    pending = [a for a in all_achievements if a.id not in already_earned_ids]

    if not pending:
        return []

    total_completed = await _count_completed_lessons(db, user_id)
    area_completed = await _count_completed_by_area(db, user_id, completed_lesson.content_area)
    total_in_area = await _count_published_in_area(db, completed_lesson.content_area)
    first_in_area = area_completed == 1

    newly_earned = []
    for achievement in pending:
        earned = False

        if achievement.trigger_type == TriggerType.lesson_count:
            earned = total_completed >= achievement.threshold

        elif achievement.trigger_type == TriggerType.area_first:
            earned = (
                achievement.content_area == completed_lesson.content_area.value
                and first_in_area
            )

        elif achievement.trigger_type == TriggerType.area_complete:
            earned = (
                achievement.content_area == completed_lesson.content_area.value
                and total_in_area > 0
                and area_completed >= total_in_area
            )

        if earned:
            db.add(UserAchievement(user_id=user_id, achievement_id=achievement.id))
            newly_earned.append(achievement.key)
            logger.info("Logro desbloqueado: user_id=%s key=%s", user_id, achievement.key)

    if newly_earned:
        await db.flush()

    return newly_earned


async def evaluate_after_assessment(db: AsyncSession, user_id: uuid.UUID) -> list[str]:
    """Evalúa logros disparados por completar la evaluación inicial."""
    all_achievements = await _get_all_achievements(db)
    already_earned_ids = await _get_earned_ids(db, user_id)

    newly_earned = []
    for achievement in all_achievements:
        if achievement.id in already_earned_ids:
            continue
        if achievement.trigger_type == TriggerType.assessment_complete:
            db.add(UserAchievement(user_id=user_id, achievement_id=achievement.id))
            newly_earned.append(achievement.key)
            logger.info("Logro desbloqueado: user_id=%s key=%s", user_id, achievement.key)

    if newly_earned:
        await db.flush()

    return newly_earned


async def get_all_with_status(
    db: AsyncSession, user_id: uuid.UUID
) -> list[tuple[Achievement, bool, datetime | None]]:
    """Devuelve todos los logros con (achievement, earned, earned_at)."""
    all_achievements = await _get_all_achievements(db)
    result = await db.execute(
        select(UserAchievement).where(UserAchievement.user_id == user_id)
    )
    earned_map = {ua.achievement_id: ua.earned_at for ua in result.scalars().all()}

    return [
        (a, a.id in earned_map, earned_map.get(a.id))
        for a in all_achievements
    ]


# ---------------------------------------------------------------------------
# Helpers privados
# ---------------------------------------------------------------------------

async def _get_all_achievements(db: AsyncSession) -> list[Achievement]:
    result = await db.execute(select(Achievement))
    return result.scalars().all()


async def _get_earned_ids(db: AsyncSession, user_id: uuid.UUID) -> set[uuid.UUID]:
    result = await db.execute(
        select(UserAchievement.achievement_id).where(UserAchievement.user_id == user_id)
    )
    return set(result.scalars().all())


async def _count_completed_lessons(db: AsyncSession, user_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.count()).where(
            UserProgress.user_id == user_id,
            UserProgress.completed == True,
        )
    )
    return result.scalar_one()


async def _count_completed_by_area(
    db: AsyncSession, user_id: uuid.UUID, area: ContentArea
) -> int:
    result = await db.execute(
        select(func.count())
        .select_from(UserProgress)
        .join(Lesson, Lesson.id == UserProgress.lesson_id)
        .where(
            UserProgress.user_id == user_id,
            UserProgress.completed == True,
            Lesson.content_area == area,
        )
    )
    return result.scalar_one()


async def _count_published_in_area(db: AsyncSession, area: ContentArea) -> int:
    result = await db.execute(
        select(func.count()).where(
            Lesson.content_area == area,
            Lesson.is_published == True,
        )
    )
    return result.scalar_one()
