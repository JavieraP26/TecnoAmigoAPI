import uuid
from datetime import datetime, timezone
from sqlalchemy import SmallInteger, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


class AssessmentResponse(Base):
    """Respuestas de la evaluación inicial. Generan el competency_map del usuario."""
    __tablename__ = "assessment_responses"
    __table_args__ = (UniqueConstraint("user_id", "question_key"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    # Ejemplos: "whatsapp_uso", "banca_online", "video_llamada", "tramites_web"
    question_key: Mapped[str] = mapped_column(String(50), nullable=False)
    # 0 = nunca lo hice, 1 = lo hice con ayuda, 2 = lo hago solo
    answer_value: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    answered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
