import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator
from app.models.user import JourneyStage


class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    phone_number: str
    full_name: str | None
    age: int | None
    city: str | None
    avatar_url: str | None
    preferred_lesson_duration: int
    reminders_enabled: bool
    reminder_hour: int
    journey_stage: JourneyStage
    competency_map: dict
    created_at: datetime


class UserProfileUpdate(BaseModel):
    full_name: str | None = None
    age: int | None = None
    city: str | None = None
    avatar_url: str | None = None
    preferred_lesson_duration: int | None = None
    reminders_enabled: bool | None = None
    reminder_hour: int | None = None

    @field_validator("preferred_lesson_duration")
    @classmethod
    def validate_duration(cls, v: int | None) -> int | None:
        if v is not None and v not in (5, 8, 12):
            raise ValueError("La duración debe ser 5, 8 o 12 minutos.")
        return v

    @field_validator("reminder_hour")
    @classmethod
    def validate_hour(cls, v: int | None) -> int | None:
        if v is not None and not (0 <= v <= 23):
            raise ValueError("La hora debe estar entre 0 y 23.")
        return v

    @field_validator("age")
    @classmethod
    def validate_age(cls, v: int | None) -> int | None:
        if v is not None and not (18 <= v <= 120):
            raise ValueError("Ingresa una edad válida.")
        return v
