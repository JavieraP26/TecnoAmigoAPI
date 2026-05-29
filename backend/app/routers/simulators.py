import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.simulator import (
    SimulatorResponse,
    StartSessionRequest,
    UpdateSessionRequest,
    SessionResponse,
)
from app.services import simulator_service

router = APIRouter(prefix="/simulators", tags=["simuladores"])


@router.get("", response_model=list[SimulatorResponse])
async def get_catalog(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await simulator_service.get_catalog(db)


@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def start_session(
    body: StartSessionRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await simulator_service.start_session(db, user.id, body.simulator_slug)


@router.patch("/sessions/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: uuid.UUID,
    body: UpdateSessionRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await simulator_service.update_session(db, user.id, session_id, body.steps_completed)


@router.post("/sessions/{session_id}/complete", response_model=SessionResponse)
async def complete_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await simulator_service.complete_session(db, user.id, session_id)
