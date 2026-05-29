"""
Peticiones de aprendizaje: los usuarios piden qué quieren aprender.
Sus votos priorizan el roadmap de contenido — son ellos quienes deciden qué viene después.
"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.community import LearningRequest, RequestVote, RequestStatus
from app.core.exceptions import ConflictError, NotFoundError
from app.core.logging_config import get_logger
from app.schemas.request import CreateLearningRequest, LearningRequestResponse, SimilarRequestInfo

logger = get_logger(__name__)

# Palabras vacías en español que no aportan al matching de similitud
_STOPWORDS = {
    "como", "el", "la", "los", "las", "un", "una", "de", "en", "y", "a",
    "que", "quiero", "aprender", "saber", "usar", "poder", "hacer", "con",
    "para", "me", "mi", "si", "no", "es", "se", "su", "al", "del", "lo",
    "le", "les", "por", "pero", "más", "sin", "sobre", "también", "hay",
}

# Umbral mínimo de similitud (0.0-1.0) para considerar que dos peticiones se parecen
_SIMILARITY_THRESHOLD = 0.25


async def create_request(
    db: AsyncSession,
    user_id: uuid.UUID,
    data: CreateLearningRequest,
) -> tuple[LearningRequest, SimilarRequestInfo | None]:
    """
    Crea la petición. Si existe una similar activa, la devuelve con su porcentaje
    de similitud para que el frontend pueda informarle amablemente al usuario.
    Devuelve (nueva_peticion, similar_info_o_None).
    """
    similar, similarity_pct = await _find_most_similar(db, data.description)

    request = LearningRequest(
        user_id=user_id,
        description=data.description,
        category=data.category,
        votes=1,
    )
    db.add(request)
    await db.flush()

    # El creador vota automáticamente su propia petición
    db.add(RequestVote(request_id=request.id, user_id=user_id))
    await db.commit()
    await db.refresh(request)

    similar_info = None
    if similar:
        similar_info = SimilarRequestInfo(
            id=similar.id,
            description=similar.description,
            status=similar.status,
            votes=similar.votes,
            similarity_pct=similarity_pct,
        )
        logger.info(
            "Petición similar encontrada: nueva=%s similar=%s similitud=%d%%",
            request.id, similar.id, similarity_pct,
        )

    logger.info("Petición creada: user_id=%s id=%s", user_id, request.id)
    return request, similar_info


async def list_requests(
    db: AsyncSession,
    user_id: uuid.UUID,
    limit: int = 20,
    offset: int = 0,
) -> list[LearningRequestResponse]:
    result = await db.execute(
        select(LearningRequest)
        .order_by(LearningRequest.votes.desc(), LearningRequest.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    requests = result.scalars().all()
    voted_ids = await _get_voted_ids(db, user_id)

    return [
        LearningRequestResponse(
            id=r.id,
            description=r.description,
            category=r.category,
            votes=r.votes,
            status=r.status,
            is_mine=r.user_id == user_id,
            already_voted=r.id in voted_ids,
            created_at=r.created_at,
        )
        for r in requests
    ]


async def vote_request(
    db: AsyncSession,
    user_id: uuid.UUID,
    request_id: uuid.UUID,
) -> LearningRequestResponse:
    result = await db.execute(
        select(LearningRequest).where(LearningRequest.id == request_id)
    )
    request = result.scalar_one_or_none()
    if not request:
        raise NotFoundError(
            "No encontramos esa petición. Puede que ya no esté disponible.",
            detail=f"request_id={request_id}",
        )

    existing = await db.execute(
        select(RequestVote).where(
            RequestVote.request_id == request_id,
            RequestVote.user_id == user_id,
        )
    )
    if existing.scalar_one_or_none():
        raise ConflictError("Ya apoyaste esta petición. ¡Gracias por participar!")

    db.add(RequestVote(request_id=request_id, user_id=user_id))
    request.votes += 1
    await db.commit()

    logger.info(
        "Voto registrado: user_id=%s request_id=%s total=%d",
        user_id, request_id, request.votes,
    )
    return LearningRequestResponse(
        id=request.id,
        description=request.description,
        category=request.category,
        votes=request.votes,
        status=request.status,
        is_mine=request.user_id == user_id,
        already_voted=True,
        created_at=request.created_at,
    )


# ---------------------------------------------------------------------------
# Similitud por índice de Jaccard sobre palabras clave
# ---------------------------------------------------------------------------

async def _find_most_similar(
    db: AsyncSession,
    description: str,
) -> tuple[LearningRequest | None, int]:
    """
    Busca la petición activa más parecida a la nueva descripción.
    Devuelve (peticion_o_None, porcentaje_similitud).
    Usa similitud de Jaccard sobre palabras clave (sin stopwords).
    """
    result = await db.execute(
        select(LearningRequest).where(
            LearningRequest.status.in_([RequestStatus.received, RequestStatus.in_development])
        )
    )
    existing = result.scalars().all()

    new_words = _keywords(description)
    if not new_words:
        return None, 0

    best: LearningRequest | None = None
    best_score = 0.0

    for req in existing:
        score = _jaccard(new_words, _keywords(req.description))
        if score > best_score:
            best_score = score
            best = req

    if best_score >= _SIMILARITY_THRESHOLD:
        return best, round(best_score * 100)

    return None, 0


def _keywords(text: str) -> set[str]:
    return {
        w for w in text.lower().split()
        if w not in _STOPWORDS and len(w) > 2
    }


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


async def _get_voted_ids(db: AsyncSession, user_id: uuid.UUID) -> set[uuid.UUID]:
    result = await db.execute(
        select(RequestVote.request_id).where(RequestVote.user_id == user_id)
    )
    return set(result.scalars().all())
