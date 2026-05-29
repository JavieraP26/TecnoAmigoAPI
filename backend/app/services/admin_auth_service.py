"""
Autenticación de administrador con dos factores:
  1. email + contraseña → pre-auth token (5 min)
  2. código TOTP → admin token (2h)

El TOTP se configura en el primer login (la app devuelve el URI para escanear con
Google Authenticator o Authy). Desde el segundo login en adelante solo pide el código.
"""
import uuid

import bcrypt
import pyotp
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.admin import AdminUser
from app.core.security import (
    create_pre_auth_token,
    create_admin_token,
    decode_pre_auth_token,
)
from app.core.exceptions import UnauthorizedError
from app.core.logging_config import get_logger

logger = get_logger(__name__)

ISSUER_NAME = "TecnoAmigo Admin"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


async def login(db: AsyncSession, email: str, password: str) -> tuple[str, str | None]:
    """
    Valida credenciales y devuelve (pre_auth_token, totp_setup_uri).
    totp_setup_uri es None cuando TOTP ya está configurado.
    """
    result = await db.execute(select(AdminUser).where(AdminUser.email == email))
    admin = result.scalar_one_or_none()

    if not admin or not _verify_password(password, admin.password_hash):
        logger.warning("Intento de login admin fallido para: %s", email)
        raise UnauthorizedError("Credenciales incorrectas.")

    pre_auth_token = create_pre_auth_token(admin.id)

    if not admin.totp_secret:
        secret = pyotp.random_base32()
        admin.totp_secret = secret
        await db.commit()
        totp_uri = pyotp.TOTP(secret).provisioning_uri(
            name=admin.email, issuer_name=ISSUER_NAME
        )
        logger.info("Primer login admin — TOTP pendiente de configurar: %s", email)
        return pre_auth_token, totp_uri

    logger.info("Login admin (paso 1 OK): %s", email)
    return pre_auth_token, None


async def verify_mfa(db: AsyncSession, pre_auth_token: str, totp_code: str) -> str:
    """
    Verifica el código TOTP y devuelve el token de admin completo.
    En el primer uso habilita TOTP definitivamente.
    """
    from jwt.exceptions import InvalidTokenError
    try:
        data = decode_pre_auth_token(pre_auth_token)
    except (InvalidTokenError, Exception):
        raise UnauthorizedError("Token de pre-autenticación inválido o expirado.")

    admin_id = uuid.UUID(data["sub"])
    result = await db.execute(select(AdminUser).where(AdminUser.id == admin_id))
    admin = result.scalar_one_or_none()

    if not admin or not admin.totp_secret:
        raise UnauthorizedError("Sesión inválida.")

    totp = pyotp.TOTP(admin.totp_secret)
    if not totp.verify(totp_code, valid_window=1):
        logger.warning("Código TOTP incorrecto para admin_id=%s", admin_id)
        raise UnauthorizedError("Código de verificación incorrecto.")

    if not admin.totp_enabled:
        admin.totp_enabled = True

    from datetime import datetime, timezone
    admin.last_login_at = datetime.now(timezone.utc)
    await db.commit()

    logger.info("Login admin completado (MFA OK): admin_id=%s", admin_id)
    return create_admin_token(admin.id)


