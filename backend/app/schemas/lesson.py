import uuid
from pydantic import BaseModel, ConfigDict
from app.models.content import ModuleType, ContentArea


class LessonSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    content_area: ContentArea
    module_type: ModuleType
    duration_minutes: int
    thumbnail_url: str | None
    description: str | None
    has_exportable_summary: bool
    # Calculados por el service según el usuario actual
    is_available: bool = True
    completion_pct: int = 0
    completed: bool = False


class LessonDetail(LessonSummary):
    prerequisite_id: uuid.UUID | None
    simulator_id: uuid.UUID | None
