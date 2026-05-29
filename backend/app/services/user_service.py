import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.core.exceptions import NotFoundError
from app.core.logging_config import get_logger
from app.schemas.user import UserProfileUpdate

logger = get_logger(__name__)


async def get_profile(db: AsyncSession, user_id: uuid.UUID) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        logger.error("Perfil no encontrado: user_id=%s", user_id)
        raise NotFoundError("Usuario no encontrado.", detail=f"user_id={user_id}")
    return user


async def update_profile(
    db: AsyncSession, user_id: uuid.UUID, data: UserProfileUpdate
) -> User:
    user = await get_profile(db, user_id)

    updates = data.model_dump(exclude_none=True)
    for field, value in updates.items():
        setattr(user, field, value)

    user.updated_at = datetime.now(timezone.utc)
    await db.commit()

    logger.info("Perfil actualizado: user_id=%s campos=%s", user_id, list(updates.keys()))
    return user
