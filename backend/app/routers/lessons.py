import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.content import ContentArea, ModuleType
from app.schemas.lesson import LessonSummary, LessonDetail
from app.services import lesson_service

router = APIRouter(prefix="/lessons", tags=["lecciones"])


@router.get("", response_model=list[LessonSummary])
async def get_catalog(
    content_area: ContentArea | None = Query(None),
    module_type: ModuleType | None = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await lesson_service.get_catalog(db, user.id, content_area, module_type)


@router.get("/{lesson_id}", response_model=LessonDetail)
async def get_lesson(
    lesson_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await lesson_service.get_lesson(db, user.id, lesson_id)
