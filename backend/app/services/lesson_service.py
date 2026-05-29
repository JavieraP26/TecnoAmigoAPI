import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.content import Lesson, ContentArea, ModuleType
from app.models.progress import UserProgress
from app.core.exceptions import NotFoundError
from app.core.logging_config import get_logger
from app.schemas.lesson import LessonSummary, LessonDetail

logger = get_logger(__name__)


async def get_catalog(
    db: AsyncSession,
    user_id: uuid.UUID,
    content_area: ContentArea | None = None,
    module_type: ModuleType | None = None,
) -> list[LessonSummary]:
    query = select(Lesson).where(Lesson.is_published == True)
    if content_area:
        query = query.where(Lesson.content_area == content_area)
    if module_type:
        query = query.where(Lesson.module_type == module_type)
    query = query.order_by(Lesson.order_index)

    result = await db.execute(query)
    lessons = result.scalars().all()

    progress_map = await _get_progress_map(db, user_id)
    completed_ids = {lid for lid, p in progress_map.items() if p.completed}

    items = []
    for lesson in lessons:
        prog = progress_map.get(lesson.id)
        is_available = _is_available(lesson, completed_ids)
        items.append(
            LessonSummary(
                id=lesson.id,
                title=lesson.title,
                content_area=lesson.content_area,
                module_type=lesson.module_type,
                duration_minutes=lesson.duration_minutes,
                thumbnail_url=lesson.thumbnail_url,
                description=lesson.description,
                has_exportable_summary=lesson.has_exportable_summary,
                is_available=is_available,
                completion_pct=prog.completion_pct if prog else 0,
                completed=prog.completed if prog else False,
            )
        )

    logger.debug("Catálogo devuelto: %d lecciones para user_id=%s", len(items), user_id)
    return items


async def get_lesson(
    db: AsyncSession,
    user_id: uuid.UUID,
    lesson_id: uuid.UUID,
) -> LessonDetail:
    result = await db.execute(
        select(Lesson).where(Lesson.id == lesson_id, Lesson.is_published == True)
    )
    lesson = result.scalar_one_or_none()
    if not lesson:
        logger.warning("Lección no encontrada: lesson_id=%s", lesson_id)
        raise NotFoundError("Lección no encontrada.", detail=f"lesson_id={lesson_id}")

    progress_map = await _get_progress_map(db, user_id)
    completed_ids = {lid for lid, p in progress_map.items() if p.completed}
    prog = progress_map.get(lesson.id)

    return LessonDetail(
        id=lesson.id,
        title=lesson.title,
        content_area=lesson.content_area,
        module_type=lesson.module_type,
        duration_minutes=lesson.duration_minutes,
        thumbnail_url=lesson.thumbnail_url,
        description=lesson.description,
        has_exportable_summary=lesson.has_exportable_summary,
        prerequisite_id=lesson.prerequisite_id,
        simulator_id=lesson.simulator_id,
        is_available=_is_available(lesson, completed_ids),
        completion_pct=prog.completion_pct if prog else 0,
        completed=prog.completed if prog else False,
    )


def _is_available(lesson: Lesson, completed_ids: set[uuid.UUID]) -> bool:
    if lesson.prerequisite_id is None:
        return True
    return lesson.prerequisite_id in completed_ids


async def _get_progress_map(
    db: AsyncSession, user_id: uuid.UUID
) -> dict[uuid.UUID, UserProgress]:
    result = await db.execute(
        select(UserProgress).where(UserProgress.user_id == user_id)
    )
    return {p.lesson_id: p for p in result.scalars().all()}
