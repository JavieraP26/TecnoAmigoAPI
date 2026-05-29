from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.schemas.admin import AdminLoginRequest, AdminLoginResponse, AdminMfaRequest, AdminTokenResponse
from app.services import admin_auth_service

router = APIRouter(prefix="/admin/auth", tags=["admin — autenticación"])


@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(
    body: AdminLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    pre_auth_token, totp_setup_uri = await admin_auth_service.login(db, body.email, body.password)
    return AdminLoginResponse(pre_auth_token=pre_auth_token, totp_setup_uri=totp_setup_uri)


@router.post("/verify-mfa", response_model=AdminTokenResponse)
async def admin_verify_mfa(
    body: AdminMfaRequest,
    db: AsyncSession = Depends(get_db),
):
    access_token = await admin_auth_service.verify_mfa(db, body.pre_auth_token, body.totp_code)
    return AdminTokenResponse(access_token=access_token)
