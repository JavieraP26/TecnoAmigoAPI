import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.achievement import TriggerType


class AchievementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    key: str
    trigger_type: TriggerType
    content_area: str | None
    threshold: int
    earned: bool = False
    earned_at: datetime | None = None


class NewlyEarned(BaseModel):
    """Logro recién desbloqueado — el frontend decide cómo celebrarlo."""
    key: str
    content_area: str | None
