import re
from pydantic import BaseModel, field_validator


_CHILE_PHONE_RE = re.compile(r"^\+569\d{8}$")


class SendSmsRequest(BaseModel):
    phone_number: str

    @field_validator("phone_number")
    @classmethod
    def validate_chilean_phone(cls, v: str) -> str:
        cleaned = v.strip().replace(" ", "")
        if not _CHILE_PHONE_RE.match(cleaned):
            raise ValueError("Ingresa un número chileno válido, por ejemplo: +56912345678")
        return cleaned


class VerifySmsRequest(BaseModel):
    phone_number: str
    code: str

    @field_validator("phone_number")
    @classmethod
    def validate_chilean_phone(cls, v: str) -> str:
        cleaned = v.strip().replace(" ", "")
        if not _CHILE_PHONE_RE.match(cleaned):
            raise ValueError("Número de teléfono inválido.")
        return cleaned

    @field_validator("code")
    @classmethod
    def validate_code_format(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 6:
            raise ValueError("El código debe tener 6 dígitos.")
        return v


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    is_new_user: bool = False


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
