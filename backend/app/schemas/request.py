import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, field_validator
from app.models.community import RequestStatus


class CreateLearningRequest(BaseModel):
    description: str
    category: str | None = None

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 10:
            raise ValueError(
                "Cuéntanos un poquito más sobre qué te gustaría aprender. "
                "Con unas pocas palabras más nos ayudas mucho."
            )
        if len(v) > 500:
            raise ValueError(
                "La descripción es un poco larga. "
                "Con un resumen breve de lo que necesitas es suficiente."
            )
        return v


class SimilarRequestInfo(BaseModel):
    id: uuid.UUID
    description: str
    status: RequestStatus
    votes: int
    # Qué tan parecida es esta petición a la nueva (0-100)
    similarity_pct: int


class LearningRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    description: str
    category: str | None
    votes: int
    status: RequestStatus
    is_mine: bool = False
    already_voted: bool = False
    created_at: datetime


class CreateRequestResponse(BaseModel):
    request: LearningRequestResponse
    # Si hay una petición similar, el frontend puede mostrar un mensaje amable
    # sugiriendo votar por ella en lugar de crear una nueva
    similar_found: SimilarRequestInfo | None = None
