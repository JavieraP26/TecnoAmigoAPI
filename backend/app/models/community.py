import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, SmallInteger, DateTime, ForeignKey, Integer, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.database import Base


class RequestStatus(str, enum.Enum):
    received = "received"           # recibida, pendiente de revisión
    in_development = "in_development"  # siendo desarrollada
    available = "available"         # ya disponible en la app


class LearningRequest(Base):
    """Los usuarios piden qué quieren aprender. Ellos priorizan el roadmap."""
    __tablename__ = "learning_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100))
    votes: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[RequestStatus] = mapped_column(
        SAEnum(RequestStatus, name="request_status_enum"),
        default=RequestStatus.received,
    )
    # Lección creada a partir de esta solicitud (cuando esté lista)
    fulfilled_by_lesson_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class RequestVote(Base):
    """Qué usuarios apoyaron qué solicitud (evita votos duplicados)."""
    __tablename__ = "request_votes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("learning_requests.id", ondelete="CASCADE")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    voted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class ExportedSummary(Base):
    """Infografías y resúmenes generados al completar módulos o al graduarse."""
    __tablename__ = "exported_summaries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    lesson_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="SET NULL"), nullable=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    # graduation = resumen final de todo su recorrido
    summary_type: Mapped[str] = mapped_column(String(50), default="lesson")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
