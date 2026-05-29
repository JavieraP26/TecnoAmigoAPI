import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, SmallInteger, Float, DateTime, JSON, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.database import Base


class JourneyStage(str, enum.Enum):
    onboarding = "onboarding"
    learning = "learning"
    practicing = "practicing"
    graduating = "graduating"
    graduated = "graduated"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255))
    age: Mapped[int | None] = mapped_column(SmallInteger)
    city: Mapped[str | None] = mapped_column(String(100))
    avatar_url: Mapped[str | None] = mapped_column(String(500))

    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    journey_stage: Mapped[JourneyStage] = mapped_column(
        SAEnum(JourneyStage, name="journey_stage_enum"),
        default=JourneyStage.onboarding,
    )

    # Mapa de competencias por área: {"comunicacion": 0.8, "banca": 0.2, ...}
    competency_map: Mapped[dict] = mapped_column(JSON, default=dict)

    preferred_lesson_duration: Mapped[int] = mapped_column(SmallInteger, default=8)
    reminders_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    reminder_hour: Mapped[int] = mapped_column(SmallInteger, default=10)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
