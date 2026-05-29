import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.community import RequestStatus
from app.models.content import ModuleType, ContentArea


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminLoginResponse(BaseModel):
    pre_auth_token: str
    totp_setup_uri: str | None = None  # presente solo en el primer login (TOTP no configurado)


class AdminMfaRequest(BaseModel):
    pre_auth_token: str
    totp_code: str = Field(..., min_length=6, max_length=6)


class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Gestión de peticiones --------------------------------------------------

class UpdateRequestStatusRequest(BaseModel):
    status: RequestStatus


# --- Gestión de simuladores -------------------------------------------------

class CreateSimulatorRequest(BaseModel):
    slug: str = Field(..., min_length=2, max_length=50)
    title: str = Field(..., min_length=2, max_length=255)
    description: str | None = None
    module_type: ModuleType
    content_area: ContentArea
    icon: str | None = None
    difficulty: int = Field(1, ge=1, le=5)


class UpdateSimulatorRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    is_active: bool | None = None
    icon: str | None = None
    difficulty: int | None = Field(None, ge=1, le=5)


# --- Stats generales --------------------------------------------------------

class AdminStats(BaseModel):
    total_users: int
    total_requests: int
    pending_requests: int
    total_simulators: int
    active_simulators: int


# --- Respuesta de usuario (vista admin) -------------------------------------

class AdminUserView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    phone_number: str
    full_name: str | None
    city: str | None
    journey_stage: str
    created_at: datetime
