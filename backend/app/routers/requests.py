import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.request import (
    CreateLearningRequest,
    CreateRequestResponse,
    LearningRequestResponse,
)
from app.services import request_service

router = APIRouter(prefix="/requests", tags=["peticiones de aprendizaje"])


@router.get("", response_model=list[LearningRequestResponse])
async def list_requests(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await request_service.list_requests(db, user.id)


@router.post("", response_model=CreateRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_request(
    body: CreateLearningRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    request, similar_info = await request_service.create_request(db, user.id, body)

    return CreateRequestResponse(
        request=LearningRequestResponse(
            id=request.id,
            description=request.description,
            category=request.category,
            votes=request.votes,
            status=request.status,
            is_mine=True,
            already_voted=True,
            created_at=request.created_at,
        ),
        similar_found=similar_info,
    )


@router.post("/{request_id}/vote", response_model=LearningRequestResponse)
async def vote_request(
    request_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await request_service.vote_request(db, user.id, request_id)
