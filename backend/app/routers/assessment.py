from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.assessment import AssessmentRequest, AssessmentResult
from app.services import assessment_service
from app.services.assessment_service import QUESTIONS

router = APIRouter(prefix="/assessment", tags=["evaluación inicial"])


@router.get("/questions")
async def get_questions(_: User = Depends(get_current_user)):
    """Devuelve las preguntas disponibles para la evaluación inicial."""
    return [
        {"key": key, "area": area.value}
        for key, area in QUESTIONS.items()
    ]


@router.post("", response_model=AssessmentResult)
async def submit_assessment(
    body: AssessmentRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await assessment_service.submit_assessment(db, user.id, body)
