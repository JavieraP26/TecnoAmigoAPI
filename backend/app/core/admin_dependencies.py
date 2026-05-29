import uuid

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.dependencies import get_db
from app.core.security import decode_admin_token
from app.core.exceptions import UnauthorizedError
from app.models.admin import AdminUser

_oauth2 = OAuth2PasswordBearer(tokenUrl="/admin/auth/login")


async def get_current_admin(
    token: str = Depends(_oauth2),
    db: AsyncSession = Depends(get_db),
) -> AdminUser:
    from jwt.exceptions import InvalidTokenError
    try:
        data = decode_admin_token(token)
    except (InvalidTokenError, Exception):
        raise UnauthorizedError("Token de administrador inválido o expirado.")

    admin_id = uuid.UUID(data["sub"])
    result = await db.execute(select(AdminUser).where(AdminUser.id == admin_id))
    admin = result.scalar_one_or_none()
    if not admin:
        raise UnauthorizedError("Administrador no encontrado.")
    return admin
