import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.content import SimulatorCatalog
from app.models.progress import SimulatorSession, UserActivity
from app.core.exceptions import NotFoundError, ConflictError
from app.core.logging_config import get_logger

logger = get_logger(__name__)


async def get_catalog(db: AsyncSession) -> list[SimulatorCatalog]:
    result = await db.execute(
        select(SimulatorCatalog)
        .where(SimulatorCatalog.is_active == True)
        .order_by(SimulatorCatalog.title)
    )
    return result.scalars().all()


async def start_session(
    db: AsyncSession,
    user_id: uuid.UUID,
    simulator_slug: str,
) -> SimulatorSession:
    simulator = await _get_simulator(db, simulator_slug)

    session = SimulatorSession(
        user_id=user_id,
        simulator_id=simulator.id,
        steps_completed=0,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    logger.info("Sesión iniciada: user_id=%s simulator=%s session_id=%s", user_id, simulator_slug, session.id)
    return session


async def update_session(
    db: AsyncSession,
    user_id: uuid.UUID,
    session_id: uuid.UUID,
    steps_completed: int,
) -> SimulatorSession:
    session = await _get_active_session(db, user_id, session_id)
    session.steps_completed = steps_completed
    await db.commit()

    logger.debug("Sesión actualizada: session_id=%s pasos=%d", session_id, steps_completed)
    return session


async def complete_session(
    db: AsyncSession,
    user_id: uuid.UUID,
    session_id: uuid.UUID,
) -> SimulatorSession:
    session = await _get_active_session(db, user_id, session_id)

    now = datetime.now(timezone.utc)
    session.completed = True
    session.ended_at = now

    await _record_activity(db, user_id, now.date())
    await db.commit()

    logger.info("Sesión completada: user_id=%s session_id=%s", user_id, session_id)
    return session


async def _get_simulator(db: AsyncSession, slug: str) -> SimulatorCatalog:
    result = await db.execute(
        select(SimulatorCatalog).where(
            SimulatorCatalog.slug == slug,
            SimulatorCatalog.is_active == True,
        )
    )
    simulator = result.scalar_one_or_none()
    if not simulator:
        logger.warning("Simulador no encontrado: slug=%s", slug)
        raise NotFoundError(
            "Este simulador no está disponible.",
            detail=f"slug={slug}",
        )
    return simulator


async def _get_active_session(
    db: AsyncSession,
    user_id: uuid.UUID,
    session_id: uuid.UUID,
) -> SimulatorSession:
    result = await db.execute(
        select(SimulatorSession).where(
            SimulatorSession.id == session_id,
            SimulatorSession.user_id == user_id,
            SimulatorSession.completed == False,
        )
    )
    session = result.scalar_one_or_none()
    if not session:
        logger.warning("Sesión no encontrada o ya completada: session_id=%s", session_id)
        raise NotFoundError(
            "Sesión no encontrada o ya finalizada.",
            detail=f"session_id={session_id}",
        )
    return session


async def _record_activity(db: AsyncSession, user_id: uuid.UUID, today) -> None:
    from datetime import date as date_type
    result = await db.execute(
        select(UserActivity).where(UserActivity.user_id == user_id)
    )
    activity = result.scalar_one_or_none()
    if not activity:
        db.add(UserActivity(
            user_id=user_id,
            first_visit_date=today,
            last_visit_date=today,
            total_active_days=1,
        ))
    elif activity.last_visit_date != today:
        activity.total_active_days += 1
        activity.last_visit_date = today
        activity.updated_at = datetime.now(timezone.utc)
