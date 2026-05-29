import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class ProgressUpdate(BaseModel):
    completion_pct: int = Field(..., ge=0, le=100)


class ProgressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    lesson_id: uuid.UUID
    completion_pct: int
    completed: bool
    completed_at: datetime | None
    last_watched_at: datetime


class CompletionResponse(ProgressResponse):
    """Respuesta de /complete — incluye logros desbloqueados para que el frontend celebre."""
    newly_earned_achievements: list[str] = []  # lista de keys
