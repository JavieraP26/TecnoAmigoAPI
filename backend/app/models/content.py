import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, SmallInteger, Text, DateTime, ForeignKey, JSON, Enum as SAEnum, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import enum

from app.database import Base


class ModuleType(str, enum.Enum):
    simulator = "simulator"       # práctica interactiva (WhatsApp, BancoEstado)
    guide = "guide"               # guía paso a paso (abrir PDF, dónde se guardan archivos)
    safety = "safety"             # seguridad digital (estafas, virus, llamadas maliciosas)
    procedure = "procedure"       # trámites (hora médica, FONASA, Registro Civil)


class ContentArea(str, enum.Enum):
    comunicacion = "comunicacion"
    banca = "banca"
    seguridad = "seguridad"
    gobierno = "gobierno"
    mi_telefono = "mi_telefono"


class SimulatorCatalog(Base):
    """Un simulador es un módulo interactivo registrado dinámicamente."""
    __tablename__ = "simulator_catalog"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    module_type: Mapped[ModuleType] = mapped_column(
        SAEnum(ModuleType, name="module_type_enum"), nullable=False
    )
    content_area: Mapped[ContentArea] = mapped_column(
        SAEnum(ContentArea, name="content_area_enum"), nullable=False
    )
    icon: Mapped[str | None] = mapped_column(String(50))
    difficulty: Mapped[int] = mapped_column(SmallInteger, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # Configuración libre por simulador (pasos, URLs, datos de práctica, etc.)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content_area: Mapped[ContentArea] = mapped_column(
        SAEnum(ContentArea, name="content_area_enum"), nullable=False
    )
    module_type: Mapped[ModuleType] = mapped_column(
        SAEnum(ModuleType, name="module_type_enum"), nullable=False
    )
    duration_minutes: Mapped[int] = mapped_column(SmallInteger, default=8)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    # ID del simulador que esta lección practica (si aplica)
    simulator_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("simulator_catalog.id", ondelete="SET NULL"), nullable=True
    )
    # Lección que debe completarse antes (grafo de aprendizaje)
    prerequisite_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("lessons.id", ondelete="SET NULL"), nullable=True
    )
    order_index: Mapped[int] = mapped_column(SmallInteger, default=0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    # Si al completar genera infografía descargable
    has_exportable_summary: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
