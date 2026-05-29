import uuid
import enum
from datetime import datetime, timezone
from sqlalchemy import String, SmallInteger, DateTime, ForeignKey, UniqueConstraint, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class TriggerType(str, enum.Enum):
    lesson_count = "lesson_count"           # N lecciones en total (threshold = N)
    area_first = "area_first"               # primera lección de un área
    area_complete = "area_complete"         # todas las lecciones de un área
    assessment_complete = "assessment_complete"


class Achievement(Base):
    __tablename__ = "achievements"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Frontend usa key para mostrar título, icono y descripción en el idioma que quiera
    key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    trigger_type: Mapped[TriggerType] = mapped_column(
        SAEnum(TriggerType, name="trigger_type_enum"), nullable=False
    )
    # Solo para area_first y area_complete — NULL para logros transversales
    content_area: Mapped[str | None] = mapped_column(String(50))
    # Para lesson_count: cuántas lecciones se necesitan
    threshold: Mapped[int] = mapped_column(SmallInteger, default=1)


class UserAchievement(Base):
    __tablename__ = "user_achievements"
    __table_args__ = (UniqueConstraint("user_id", "achievement_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    achievement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("achievements.id", ondelete="CASCADE")
    )
    earned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
