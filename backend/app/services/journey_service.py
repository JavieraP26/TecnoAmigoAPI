"""
Estado del arco completo del usuario y lógica de graduación.

El usuario se gradúa cuando alcanza el 85% de logros disponibles.
La graduación genera un PDF resumen y marca el fin del uso activo de la app.
"""
import uuid
from datetime import date, datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.user import User, JourneyStage
from app.models.content import Lesson, ContentArea
from app.models.progress import UserProgress, UserActivity
from app.models.achievement import Achievement, UserAchievement
from app.models.community import ExportedSummary, LearningRequest, RequestVote, RequestStatus
from app.core.exceptions import NotFoundError, ConflictError, ValidationError
from app.core.logging_config import get_logger
from app.services.pdf_service import PdfService
from app.schemas.journey import JourneyStatus, AreaProgress, GraduationResponse

logger = get_logger(__name__)

GRADUATION_THRESHOLD = 0.85


async def get_journey_status(db: AsyncSession, user_id: uuid.UUID) -> JourneyStatus:
    user = await _get_user(db, user_id)

    achievements_earned, achievements_total = await _count_achievements(db, user_id)
    achievement_pct = round(achievements_earned / achievements_total * 100) if achievements_total else 0

    areas_progress = await _build_areas_progress(db, user_id, user.competency_map)
    total_completed = await _count_total_completed(db, user_id)
    activity = await _get_activity(db, user_id)
    pending_voted = await _count_pending_voted_requests(db, user_id)

    return JourneyStatus(
        stage=user.journey_stage,
        areas_progress=areas_progress,
        achievements_earned=achievements_earned,
        achievements_total=achievements_total,
        achievement_pct=achievement_pct,
        ready_to_graduate=(
            achievement_pct >= round(GRADUATION_THRESHOLD * 100)
            and user.journey_stage not in (JourneyStage.graduating, JourneyStage.graduated)
        ),
        total_lessons_completed=total_completed,
        total_active_days=activity.total_active_days if activity else 0,
        first_visit_date=activity.first_visit_date.isoformat() if activity else None,
        pending_voted_requests=pending_voted,
    )


async def graduate(
    db: AsyncSession,
    user_id: uuid.UUID,
    pdf: PdfService,
) -> GraduationResponse:
    user = await _get_user(db, user_id)

    if user.journey_stage == JourneyStage.graduated:
        raise ConflictError("Ya completaste tu camino en TecnoAmigo. ¡Felicitaciones!")

    achievements_earned, achievements_total = await _count_achievements(db, user_id)
    achievement_pct = round(achievements_earned / achievements_total * 100) if achievements_total else 0

    if achievement_pct < round(GRADUATION_THRESHOLD * 100):
        raise ValidationError(
            f"Aún te faltan algunos logros para graduarte. "
            f"Ya tienes el {achievement_pct}% — ¡sigue así, estás muy cerca!",
            detail=f"user_id={user_id} pct={achievement_pct}",
        )

    total_completed = await _count_total_completed(db, user_id)
    activity = await _get_activity(db, user_id)
    completed_areas = await _get_completed_areas(db, user_id)

    today = date.today()
    pdf_data = {
        "user_id": str(user_id),
        "full_name": user.full_name,
        "city": user.city,
        "first_visit_date": activity.first_visit_date.isoformat() if activity else today.isoformat(),
        "graduation_date": today.isoformat(),
        "completed_areas": [a.value for a in completed_areas],
        "achievements_earned": achievements_earned,
        "achievements_total": achievements_total,
        "total_lessons_completed": total_completed,
        "total_active_days": activity.total_active_days if activity else 0,
    }

    file_url = await pdf.generate_graduation_summary(pdf_data)

    summary = ExportedSummary(
        user_id=user_id,
        title="Mi recorrido en TecnoAmigo",
        file_url=file_url,
        summary_type="graduation",
    )
    db.add(summary)

    user.journey_stage = JourneyStage.graduated
    await db.commit()
    await db.refresh(summary)

    logger.info("Graduación completada: user_id=%s pct=%d%%", user_id, achievement_pct)

    return GraduationResponse(
        summary_id=summary.id,
        file_url=file_url,
        achievement_pct=achievement_pct,
        total_lessons_completed=total_completed,
        total_active_days=activity.total_active_days if activity else 0,
    )


async def get_summaries(db: AsyncSession, user_id: uuid.UUID) -> list[ExportedSummary]:
    result = await db.execute(
        select(ExportedSummary)
        .where(ExportedSummary.user_id == user_id)
        .order_by(ExportedSummary.created_at.desc())
    )
    return result.scalars().all()


# ---------------------------------------------------------------------------
# Helpers privados
# ---------------------------------------------------------------------------

async def _get_user(db: AsyncSession, user_id: uuid.UUID) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("Usuario no encontrado.", detail=f"user_id={user_id}")
    return user


async def _count_achievements(db: AsyncSession, user_id: uuid.UUID) -> tuple[int, int]:
    total_r = await db.execute(select(func.count()).select_from(Achievement))
    earned_r = await db.execute(
        select(func.count()).where(UserAchievement.user_id == user_id)
    )
    return earned_r.scalar_one(), total_r.scalar_one()


async def _count_total_completed(db: AsyncSession, user_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.count()).where(
            UserProgress.user_id == user_id,
            UserProgress.completed == True,
        )
    )
    return result.scalar_one()


async def _get_activity(db: AsyncSession, user_id: uuid.UUID) -> UserActivity | None:
    result = await db.execute(
        select(UserActivity).where(UserActivity.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def _build_areas_progress(
    db: AsyncSession,
    user_id: uuid.UUID,
    competency_map: dict,
) -> dict[str, AreaProgress]:
    areas = {}
    for area in ContentArea:
        total_r = await db.execute(
            select(func.count()).where(
                Lesson.content_area == area,
                Lesson.is_published == True,
            )
        )
        completed_r = await db.execute(
            select(func.count())
            .select_from(UserProgress)
            .join(Lesson, Lesson.id == UserProgress.lesson_id)
            .where(
                UserProgress.user_id == user_id,
                UserProgress.completed == True,
                Lesson.content_area == area,
            )
        )
        total = total_r.scalar_one()
        completed = completed_r.scalar_one()

        areas[area.value] = AreaProgress(
            initial_score=competency_map.get(area.value),
            lessons_completed=completed,
            total_lessons=total,
            pct_complete=round(completed / total * 100) if total else 0,
        )
    return areas


async def _count_pending_voted_requests(db: AsyncSession, user_id: uuid.UUID) -> int:
    result = await db.execute(
        select(func.count())
        .select_from(RequestVote)
        .join(LearningRequest, LearningRequest.id == RequestVote.request_id)
        .where(
            RequestVote.user_id == user_id,
            LearningRequest.status != RequestStatus.available,
        )
    )
    return result.scalar_one()


async def _get_completed_areas(db: AsyncSession, user_id: uuid.UUID) -> list[ContentArea]:
    completed = []
    for area in ContentArea:
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
        if result.scalar_one() > 0:
            completed.append(area)
    return completed
