import uuid
from datetime import datetime, date, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.content import Lesson
from app.models.progress import UserProgress, UserActivity
from app.core.exceptions import NotFoundError, ConflictError
from app.core.logging_config import get_logger
from app.schemas.progress import ProgressResponse

logger = get_logger(__name__)


async def start_lesson(
    db: AsyncSession,
    user_id: uuid.UUID,
    lesson_id: uuid.UUID,
) -> ProgressResponse:
    await _assert_lesson_exists(db, lesson_id)

    result = await db.execute(
        select(UserProgress).where(
            UserProgress.user_id == user_id,
            UserProgress.lesson_id == lesson_id,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        if existing.completed:
            raise ConflictError("Esta lección ya fue completada.")
        existing.last_watched_at = datetime.now(timezone.utc)
        await db.commit()
        logger.info("Lección reanudada: user_id=%s lesson_id=%s", user_id, lesson_id)
        return ProgressResponse.model_validate(existing)

    progress = UserProgress(user_id=user_id, lesson_id=lesson_id, completion_pct=0)
    db.add(progress)
    await db.commit()
    await db.refresh(progress)
    logger.info("Lección iniciada: user_id=%s lesson_id=%s", user_id, lesson_id)
    return ProgressResponse.model_validate(progress)


async def update_progress(
    db: AsyncSession,
    user_id: uuid.UUID,
    lesson_id: uuid.UUID,
    completion_pct: int,
) -> ProgressResponse:
    progress = await _get_active_progress(db, user_id, lesson_id)
    progress.completion_pct = completion_pct
    progress.last_watched_at = datetime.now(timezone.utc)
    await db.commit()
    logger.debug(
        "Progreso actualizado: user_id=%s lesson_id=%s pct=%d",
        user_id, lesson_id, completion_pct,
    )
    return ProgressResponse.model_validate(progress)


async def complete_lesson(
    db: AsyncSession,
    user_id: uuid.UUID,
    lesson_id: uuid.UUID,
) -> ProgressResponse:
    progress = await _get_active_progress(db, user_id, lesson_id)
    now = datetime.now(timezone.utc)
    progress.completion_pct = 100
    progress.completed = True
    progress.completed_at = now
    progress.last_watched_at = now

    await _record_activity(db, user_id, now.date())
    await db.commit()

    logger.info("Lección completada: user_id=%s lesson_id=%s", user_id, lesson_id)
    return ProgressResponse.model_validate(progress)


async def get_welcome_context(db: AsyncSession, user_id: uuid.UUID) -> dict:
    """
    Devuelve contexto para que el frontend muestre un saludo cálido al volver.
    Sin contadores de racha ni presión — solo reconocimiento amable.
    """
    result = await db.execute(select(UserActivity).where(UserActivity.user_id == user_id))
    activity = result.scalar_one_or_none()

    if not activity:
        return {"returning": False, "days_since_last_visit": None, "total_active_days": 0}

    today = date.today()
    days_away = (today - activity.last_visit_date).days

    return {
        "returning": days_away > 0,
        "days_since_last_visit": days_away if days_away > 0 else None,
        "total_active_days": activity.total_active_days,
        "first_visit_date": activity.first_visit_date.isoformat(),
    }


async def _record_activity(db: AsyncSession, user_id: uuid.UUID, today: date) -> None:
    """Registra que el usuario tuvo actividad hoy. Sin contadores de racha."""
    result = await db.execute(select(UserActivity).where(UserActivity.user_id == user_id))
    activity = result.scalar_one_or_none()

    if not activity:
        db.add(UserActivity(
            user_id=user_id,
            first_visit_date=today,
            last_visit_date=today,
            total_active_days=1,
        ))
        logger.info("Primera actividad registrada: user_id=%s", user_id)
        return

    if activity.last_visit_date == today:
        return  # Ya registrada hoy, nada que hacer

    activity.total_active_days += 1
    activity.last_visit_date = today
    activity.updated_at = datetime.now(timezone.utc)
    logger.info(
        "Actividad registrada: user_id=%s días_totales=%d ausente=%d días",
        user_id,
        activity.total_active_days,
        (today - activity.last_visit_date).days,
    )


async def _assert_lesson_exists(db: AsyncSession, lesson_id: uuid.UUID) -> None:
    result = await db.execute(
        select(Lesson).where(Lesson.id == lesson_id, Lesson.is_published == True)
    )
    if not result.scalar_one_or_none():
        logger.warning("Intento de acceso a lección inexistente: lesson_id=%s", lesson_id)
        raise NotFoundError("Lección no encontrada.", detail=f"lesson_id={lesson_id}")


async def _get_active_progress(
    db: AsyncSession,
    user_id: uuid.UUID,
    lesson_id: uuid.UUID,
) -> UserProgress:
    await _assert_lesson_exists(db, lesson_id)
    result = await db.execute(
        select(UserProgress).where(
            UserProgress.user_id == user_id,
            UserProgress.lesson_id == lesson_id,
        )
    )
    progress = result.scalar_one_or_none()
    if not progress:
        logger.warning("Progreso no iniciado: user_id=%s lesson_id=%s", user_id, lesson_id)
        raise NotFoundError(
            "Debes iniciar la lección antes de actualizarla.",
            detail=f"user_id={user_id} lesson_id={lesson_id}",
        )
    return progress
