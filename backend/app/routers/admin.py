import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.core.admin_dependencies import get_current_admin
from app.models.admin import AdminUser
from app.models.community import RequestStatus
from app.schemas.admin import (
    AdminStats,
    AdminUserView,
    UpdateRequestStatusRequest,
    CreateSimulatorRequest,
    UpdateSimulatorRequest,
)
from app.schemas.request import LearningRequestResponse
from app.schemas.simulator import SimulatorResponse
from app.services import admin_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStats)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    return await admin_service.get_stats(db)


# --- Peticiones -------------------------------------------------------------

@router.get("/requests", response_model=list[LearningRequestResponse])
async def list_requests(
    status: RequestStatus | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    requests = await admin_service.list_requests(db, status=status, limit=limit, offset=offset)
    return [
        LearningRequestResponse(
            id=r.id,
            description=r.description,
            category=r.category,
            votes=r.votes,
            status=r.status,
            is_mine=False,
            already_voted=False,
            created_at=r.created_at,
        )
        for r in requests
    ]


@router.patch("/requests/{request_id}/status", response_model=LearningRequestResponse)
async def update_request_status(
    request_id: uuid.UUID,
    body: UpdateRequestStatusRequest,
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    req = await admin_service.update_request_status(db, request_id, body.status)
    return LearningRequestResponse(
        id=req.id,
        description=req.description,
        category=req.category,
        votes=req.votes,
        status=req.status,
        is_mine=False,
        already_voted=False,
        created_at=req.created_at,
    )


# --- Simuladores ------------------------------------------------------------

@router.get("/simulators", response_model=list[SimulatorResponse])
async def list_simulators(
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    return await admin_service.list_simulators(db)


@router.post("/simulators", response_model=SimulatorResponse, status_code=status.HTTP_201_CREATED)
async def create_simulator(
    body: CreateSimulatorRequest,
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    return await admin_service.create_simulator(db, body)


@router.patch("/simulators/{simulator_id}", response_model=SimulatorResponse)
async def update_simulator(
    simulator_id: uuid.UUID,
    body: UpdateSimulatorRequest,
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    return await admin_service.update_simulator(db, simulator_id, body)


# --- Usuarios ---------------------------------------------------------------

@router.get("/users", response_model=list[AdminUserView])
async def list_users(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: AdminUser = Depends(get_current_admin),
):
    return await admin_service.list_users(db, limit=limit, offset=offset)
