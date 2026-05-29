import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class WelcomeContext(BaseModel):
    returning: bool
    days_since_last_visit: int | None = None
    total_active_days: int
    first_visit_date: str | None = None


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
