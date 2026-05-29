from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.journey import JourneyStatus, GraduationResponse, SummaryResponse
from app.services import journey_service
from app.services.pdf_service import PdfService, get_pdf_service

router = APIRouter(prefix="/users/me", tags=["arco del usuario"])


@router.get("/journey", response_model=JourneyStatus)
async def get_journey(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await journey_service.get_journey_status(db, user.id)


@router.post("/graduate", response_model=GraduationResponse)
async def graduate(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    pdf: PdfService = Depends(get_pdf_service),
):
    return await journey_service.graduate(db, user.id, pdf)


@router.get("/summaries", response_model=list[SummaryResponse])
async def get_summaries(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await journey_service.get_summaries(db, user.id)
