import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.models.content import ModuleType, ContentArea


class SimulatorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    slug: str
    title: str
    description: str | None
    module_type: ModuleType
    content_area: ContentArea
    icon: str | None
    difficulty: int


class StartSessionRequest(BaseModel):
    simulator_slug: str


class UpdateSessionRequest(BaseModel):
    steps_completed: int = Field(..., ge=0)


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    simulator_id: uuid.UUID
    steps_completed: int
    completed: bool
    started_at: datetime
    ended_at: datetime | None
