from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.core.limiter import limiter
from app.models.user import User
from app.schemas.auth import (
    SendSmsRequest,
    VerifySmsRequest,
    RefreshRequest,
    TokenResponse,
    AccessTokenResponse,
)
from app.services import auth_service
from app.services.sms_service import SmsService, get_sms_service

router = APIRouter(prefix="/auth", tags=["autenticación"])


@router.post("/send-sms", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("3/10minute")
async def send_sms(
    request: Request,
    body: SendSmsRequest,
    db: AsyncSession = Depends(get_db),
    sms: SmsService = Depends(get_sms_service),
):
    await auth_service.send_sms_code(body.phone_number, db, sms)


@router.post("/verify-sms", response_model=TokenResponse)
async def verify_sms(
    body: VerifySmsRequest,
    db: AsyncSession = Depends(get_db),
):
    user, access_token, refresh_token, is_new_user = await auth_service.verify_sms_and_login(
        body.phone_number, body.code, db
    )
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        is_new_user=is_new_user,
    )


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    access_token = await auth_service.refresh_access_token(body.refresh_token, db)
    return AccessTokenResponse(access_token=access_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    await auth_service.logout(body.refresh_token, db)
