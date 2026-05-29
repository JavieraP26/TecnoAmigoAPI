from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.user import UserProfile, UserProfileUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["perfil"])


@router.get("/me", response_model=UserProfile)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await user_service.get_profile(db, user.id)


@router.patch("/me", response_model=UserProfile)
async def update_profile(
    body: UserProfileUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await user_service.update_profile(db, user.id, body)
