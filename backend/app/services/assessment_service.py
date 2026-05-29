"""
Evaluación inicial → competency_map → lecciones recomendadas.

Las preguntas están definidas aquí como configuración, no en BD,
porque son parte del contrato pedagógico del producto y cambian poco.
Para agregar una pregunta: añadir una entrada a QUESTIONS.
"""
import uuid
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.models.assessment import AssessmentResponse
from app.models.content import ContentArea, Lesson
from app.models.user import User, JourneyStage
from app.core.exceptions import NotFoundError, ValidationError
from app.core.logging_config import get_logger
from app.schemas.assessment import AssessmentRequest, AssessmentResult, RecommendedLesson

logger = get_logger(__name__)

# Catálogo de preguntas: question_key → área de competencia
# answer_value: 0=nunca, 1=con ayuda, 2=solo
QUESTIONS: dict[str, ContentArea] = {
    "whatsapp_mensajes":    ContentArea.comunicacion,
    "whatsapp_fotos":       ContentArea.comunicacion,
    "videollamada":         ContentArea.comunicacion,
    "banca_consulta":       ContentArea.banca,
    "banca_transferencia":  ContentArea.banca,
    "clave_unica":          ContentArea.gobierno,
    "tramites_web":         ContentArea.gobierno,
    "guardar_archivos":     ContentArea.mi_telefono,
    "abrir_pdf":            ContentArea.mi_telefono,
    "reconocer_estafa":     ContentArea.seguridad,
    "llamadas_sospechosas": ContentArea.seguridad,
}

_AREA_THRESHOLD_TO_SKIP = 0.7  # Si supera este nivel, el área no se recomienda


async def submit_assessment(
    db: AsyncSession,
    user_id: uuid.UUID,
    request: AssessmentRequest,
) -> AssessmentResult:
    user = await _get_user(db, user_id)

    unknown_keys = {a.question_key for a in request.answers} - QUESTIONS.keys()
    if unknown_keys:
        logger.warning(
            "Evaluación con claves desconocidas: user_id=%s keys=%s", user_id, unknown_keys
        )
        raise ValidationError(
            "Algunas preguntas no son válidas.",
            detail=f"Claves desconocidas: {unknown_keys}",
        )

    # Reemplaza respuestas anteriores (permite repetir la evaluación)
    await db.execute(
        delete(AssessmentResponse).where(AssessmentResponse.user_id == user_id)
    )

    for answer in request.answers:
        db.add(AssessmentResponse(
            user_id=user_id,
            question_key=answer.question_key,
            answer_value=answer.answer_value,
        ))

    competency_map = _compute_competency_map(request.answers)
    user.competency_map = {area.value: score for area, score in competency_map.items()}

    if user.journey_stage == JourneyStage.onboarding:
        user.journey_stage = JourneyStage.learning
        logger.info("Usuario avanza a etapa 'learning': user_id=%s", user_id)

    from app.services import achievement_service

    recommendations = await _get_recommendations(db, competency_map)
    await achievement_service.evaluate_after_assessment(db, user_id)
    await db.commit()

    logger.info(
        "Evaluación completada: user_id=%s mapa=%s",
        user_id, user.competency_map,
    )
    return AssessmentResult(
        competency_map=competency_map,
        recommended_lessons=recommendations,
        journey_stage=user.journey_stage.value,
    )


def _compute_competency_map(answers: list) -> dict[ContentArea, float]:
    area_values: dict[ContentArea, list[float]] = defaultdict(list)
    for answer in answers:
        area = QUESTIONS.get(answer.question_key)
        if area:
            # Normaliza 0-2 → 0.0-1.0
            area_values[area].append(answer.answer_value / 2.0)

    return {
        area: round(sum(scores) / len(scores), 2)
        for area, scores in area_values.items()
    }


async def _get_recommendations(
    db: AsyncSession,
    competency_map: dict[ContentArea, float],
) -> list[RecommendedLesson]:
    # Áreas donde el usuario tiene menos del umbral → recomendar primera lección de esa área
    weak_areas = [
        area for area, score in competency_map.items()
        if score < _AREA_THRESHOLD_TO_SKIP
    ]

    recommendations = []
    for area in weak_areas:
        result = await db.execute(
            select(Lesson)
            .where(
                Lesson.content_area == area,
                Lesson.is_published == True,
                Lesson.prerequisite_id == None,
            )
            .order_by(Lesson.order_index)
            .limit(1)
        )
        lesson = result.scalar_one_or_none()
        if lesson:
            score = competency_map[area]
            reason = _reason_for_area(area, score)
            recommendations.append(RecommendedLesson(
                id=str(lesson.id),
                title=lesson.title,
                content_area=area,
                reason=reason,
            ))

    logger.debug("Recomendaciones generadas: %d áreas débiles", len(recommendations))
    return recommendations


def _reason_for_area(area: ContentArea, score: float) -> str:
    label = {
        ContentArea.comunicacion: "comunicarte con tu familia por WhatsApp",
        ContentArea.banca: "manejar tu banco desde el teléfono",
        ContentArea.gobierno: "hacer trámites sin salir de casa",
        ContentArea.mi_telefono: "manejar mejor tu teléfono",
        ContentArea.seguridad: "protegerte de llamadas y mensajes sospechosos",
    }.get(area, area.value)

    if score == 0.0:
        return f"Nunca has podido {label}. ¡Empecemos juntos!"
    return f"Ya tienes algo de experiencia, pero podemos ayudarte a {label} con más seguridad."


async def _get_user(db: AsyncSession, user_id: uuid.UUID) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        logger.error("Usuario no encontrado en evaluación: user_id=%s", user_id)
        raise NotFoundError("Usuario no encontrado.", detail=f"user_id={user_id}")
    return user
