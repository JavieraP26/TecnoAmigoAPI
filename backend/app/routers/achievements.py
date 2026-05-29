from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.achievement import AchievementResponse
from app.services import achievement_service

router = APIRouter(prefix="/achievements", tags=["logros"])


@router.get("", response_model=list[AchievementResponse])
async def list_achievements(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Catálogo completo con flag earned por usuario."""
    items = await achievement_service.get_all_with_status(db, user.id)
    return [
        AchievementResponse(
            id=a.id,
            key=a.key,
            trigger_type=a.trigger_type,
            content_area=a.content_area,
            threshold=a.threshold,
            earned=earned,
            earned_at=earned_at,
        )
        for a, earned, earned_at in items
    ]


@router.get("/me", response_model=list[AchievementResponse])
async def my_achievements(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Solo los logros que el usuario ya ganó."""
    items = await achievement_service.get_all_with_status(db, user.id)
    return [
        AchievementResponse(
            id=a.id,
            key=a.key,
            trigger_type=a.trigger_type,
            content_area=a.content_area,
            threshold=a.threshold,
            earned=True,
            earned_at=earned_at,
        )
        for a, earned, earned_at in items
        if earned
    ]
