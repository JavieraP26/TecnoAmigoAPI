import random
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.auth import SmsVerification, RefreshToken
from app.core.exceptions import ValidationError, UnauthorizedError, ExternalServiceError
from app.core.security import create_access_token, create_refresh_token, hash_token
from app.core.logging_config import get_logger
from app.services.sms_service import SmsService

logger = get_logger(__name__)

_CODE_TTL_MINUTES = 10


def _generate_code() -> str:
    return f"{random.randint(0, 999999):06d}"


async def send_sms_code(phone_number: str, db: AsyncSession, sms: SmsService) -> None:
    code = _generate_code()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=_CODE_TTL_MINUTES)

    verification = SmsVerification(phone_number=phone_number, code=code, expires_at=expires_at)
    db.add(verification)
    await db.commit()

    logger.info("Código SMS generado para %s", phone_number)

    try:
        await sms.send_verification_code(phone_number, code)
    except Exception as exc:
        logger.error("Fallo al enviar SMS a %s: %s", phone_number, exc, exc_info=True)
        raise ExternalServiceError(
            "No pudimos enviar el SMS. Intenta nuevamente en unos minutos.",
            detail=f"Twilio error para {phone_number}: {exc}",
        )


async def verify_sms_and_login(
    phone_number: str,
    code: str,
    db: AsyncSession,
) -> tuple[User, str, str, bool]:
    now = datetime.now(timezone.utc)

    result = await db.execute(
        select(SmsVerification)
        .where(
            SmsVerification.phone_number == phone_number,
            SmsVerification.code == code,
            SmsVerification.used == False,
            SmsVerification.expires_at > now,
        )
        .order_by(SmsVerification.created_at.desc())
        .limit(1)
    )
    verification = result.scalar_one_or_none()

    if not verification:
        logger.warning("Intento fallido de verificación SMS para %s", phone_number)
        raise ValidationError("Código incorrecto o expirado.")

    verification.used = True

    result = await db.execute(select(User).where(User.phone_number == phone_number))
    user = result.scalar_one_or_none()
    is_new_user = user is None

    if is_new_user:
        user = User(phone_number=phone_number, phone_verified=True)
        db.add(user)
        await db.flush()
        logger.info("Nuevo usuario creado: %s", phone_number)

    access_token = create_access_token(user.id)
    raw_refresh, token_hash, expires_at = create_refresh_token(user.id)

    refresh = RefreshToken(user_id=user.id, token_hash=token_hash, expires_at=expires_at)
    db.add(refresh)
    await db.commit()

    logger.info("Login exitoso: user_id=%s, nuevo=%s", user.id, is_new_user)
    return user, access_token, raw_refresh, is_new_user


async def refresh_access_token(raw_refresh_token: str, db: AsyncSession) -> str:
    from jwt.exceptions import InvalidTokenError
    from app.core.security import decode_token

    try:
        payload = decode_token(raw_refresh_token)
    except InvalidTokenError as exc:
        logger.warning("Refresh token inválido (JWT): %s", exc)
        raise UnauthorizedError("Token inválido.")

    if payload.get("type") != "refresh":
        logger.warning("Refresh token con type incorrecto: %s", payload.get("type"))
        raise UnauthorizedError("Token inválido.")

    token_hash = hash_token(raw_refresh_token)
    now = datetime.now(timezone.utc)

    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked == False,
            RefreshToken.expires_at > now,
        )
    )
    stored = result.scalar_one_or_none()
    if not stored:
        logger.warning("Refresh token no encontrado o revocado: hash=%s", token_hash[:12])
        raise UnauthorizedError("Sesión expirada. Por favor inicia sesión nuevamente.")

    user_id = uuid.UUID(payload["sub"])
    logger.info("Access token renovado: user_id=%s", user_id)
    return create_access_token(user_id)


async def logout(raw_refresh_token: str, db: AsyncSession) -> None:
    token_hash = hash_token(raw_refresh_token)

    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    stored = result.scalar_one_or_none()
    if stored:
        stored.revoked = True
        await db.commit()
        logger.info("Logout: token revocado para user_id=%s", stored.user_id)
