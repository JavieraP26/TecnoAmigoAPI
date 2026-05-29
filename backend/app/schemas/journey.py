import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.user import JourneyStage


class AreaProgress(BaseModel):
    initial_score: float | None   # score del competency_map al hacer la evaluación
    lessons_completed: int
    total_lessons: int
    pct_complete: int             # lessons_completed / total_lessons * 100


class JourneyStatus(BaseModel):
    stage: JourneyStage
    areas_progress: dict[str, AreaProgress]
    achievements_earned: int
    achievements_total: int
    achievement_pct: int
    ready_to_graduate: bool
    total_lessons_completed: int
    total_active_days: int
    first_visit_date: str | None
    pending_voted_requests: int  # peticiones apoyadas aún no disponibles como lecciones


class GraduationResponse(BaseModel):
    summary_id: uuid.UUID
    file_url: str
    achievement_pct: int
    total_lessons_completed: int
    total_active_days: int


class SummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    file_url: str
    summary_type: str
    created_at: datetime
