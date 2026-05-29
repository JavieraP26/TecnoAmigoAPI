from pydantic import BaseModel, Field
from app.models.content import ContentArea


class QuestionResponse(BaseModel):
    key: str
    area: str


class AssessmentAnswer(BaseModel):
    question_key: str
    answer_value: int = Field(..., ge=0, le=2)


class AssessmentRequest(BaseModel):
    answers: list[AssessmentAnswer]


class RecommendedLesson(BaseModel):
    id: str
    title: str
    content_area: ContentArea
    reason: str


class AssessmentResult(BaseModel):
    competency_map: dict[ContentArea, float]
    recommended_lessons: list[RecommendedLesson]
    journey_stage: str
