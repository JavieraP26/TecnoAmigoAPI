import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.progress import ProgressUpdate, ProgressResponse, CompletionResponse, WelcomeContext
from app.services import progress_service

router = APIRouter(prefix="/progress", tags=["progreso"])


@router.get("/welcome", response_model=WelcomeContext, summary="Contexto de bienvenida al abrir la app")
async def welcome_context(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Devuelve info para mostrar un saludo cálido según cuánto tiempo lleva el usuario ausente.
    Sin rachas ni presión — solo reconocimiento amable de su regreso.
    """
    return await progress_service.get_welcome_context(db, user.id)


@router.post("/{lesson_id}/start", response_model=ProgressResponse, status_code=status.HTTP_201_CREATED)
async def start_lesson(
    lesson_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await progress_service.start_lesson(db, user.id, lesson_id)


@router.patch("/{lesson_id}", response_model=ProgressResponse)
async def update_progress(
    lesson_id: uuid.UUID,
    body: ProgressUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await progress_service.update_progress(db, user.id, lesson_id, body.completion_pct)


@router.post("/{lesson_id}/complete", response_model=CompletionResponse)
async def complete_lesson(
    lesson_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await progress_service.complete_lesson(db, user.id, lesson_id)
