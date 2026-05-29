"""Operaciones de administración: peticiones, simuladores, usuarios y estadísticas."""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.community import LearningRequest, RequestStatus
from app.models.content import SimulatorCatalog, ModuleType, ContentArea
from app.models.user import User
from app.core.exceptions import NotFoundError, ConflictError
from app.core.logging_config import get_logger
from app.schemas.admin import CreateSimulatorRequest, UpdateSimulatorRequest

logger = get_logger(__name__)


# --- Peticiones de aprendizaje ----------------------------------------------

async def list_requests(
    db: AsyncSession,
    status: RequestStatus | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[LearningRequest]:
    q = select(LearningRequest).order_by(
        LearningRequest.votes.desc(), LearningRequest.created_at.desc()
    ).limit(limit).offset(offset)

    if status:
        q = q.where(LearningRequest.status == status)

    result = await db.execute(q)
    return result.scalars().all()


async def update_request_status(
    db: AsyncSession,
    request_id: uuid.UUID,
    new_status: RequestStatus,
) -> LearningRequest:
    result = await db.execute(
        select(LearningRequest).where(LearningRequest.id == request_id)
    )
    req = result.scalar_one_or_none()
    if not req:
        raise NotFoundError("Petición no encontrada.")

    req.status = new_status
    await db.commit()
    await db.refresh(req)
    logger.info("Petición %s → status=%s", request_id, new_status.value)
    return req


# --- Simuladores ------------------------------------------------------------

async def list_simulators(db: AsyncSession) -> list[SimulatorCatalog]:
    result = await db.execute(
        select(SimulatorCatalog).order_by(SimulatorCatalog.content_area, SimulatorCatalog.title)
    )
    return result.scalars().all()


async def create_simulator(db: AsyncSession, data: CreateSimulatorRequest) -> SimulatorCatalog:
    existing = await db.execute(
        select(SimulatorCatalog).where(SimulatorCatalog.slug == data.slug)
    )
    if existing.scalar_one_or_none():
        raise ConflictError(f"Ya existe un simulador con el slug '{data.slug}'.")

    sim = SimulatorCatalog(**data.model_dump())
    db.add(sim)
    await db.commit()
    await db.refresh(sim)
    logger.info("Simulador creado: slug=%s", data.slug)
    return sim


async def update_simulator(
    db: AsyncSession,
    simulator_id: uuid.UUID,
    data: UpdateSimulatorRequest,
) -> SimulatorCatalog:
    result = await db.execute(
        select(SimulatorCatalog).where(SimulatorCatalog.id == simulator_id)
    )
    sim = result.scalar_one_or_none()
    if not sim:
        raise NotFoundError("Simulador no encontrado.")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(sim, field, value)

    await db.commit()
    await db.refresh(sim)
    logger.info("Simulador actualizado: id=%s", simulator_id)
    return sim


# --- Usuarios ---------------------------------------------------------------

async def list_users(
    db: AsyncSession,
    limit: int = 50,
    offset: int = 0,
) -> list[User]:
    result = await db.execute(
        select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
    )
    return result.scalars().all()


# --- Estadísticas -----------------------------------------------------------

async def get_stats(db: AsyncSession) -> dict:
    total_users = (await db.execute(select(func.count()).select_from(User))).scalar_one()
    total_requests = (await db.execute(select(func.count()).select_from(LearningRequest))).scalar_one()
    pending_requests = (await db.execute(
        select(func.count()).where(LearningRequest.status != RequestStatus.available)
    )).scalar_one()
    total_simulators = (await db.execute(select(func.count()).select_from(SimulatorCatalog))).scalar_one()
    active_simulators = (await db.execute(
        select(func.count()).where(SimulatorCatalog.is_active == True)
    )).scalar_one()

    return {
        "total_users": total_users,
        "total_requests": total_requests,
        "pending_requests": pending_requests,
        "total_simulators": total_simulators,
        "active_simulators": active_simulators,
    }
