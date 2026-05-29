"""
Handlers globales de excepciones para FastAPI.

Regla:
  - Errores de dominio (TecnoAmigoError): log en su nivel apropiado, respuesta JSON limpia.
  - Errores no esperados (Exception): log ERROR con traceback completo, respuesta genérica.
  - Nunca exponer detalles internos al cliente.
"""
import traceback

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import TecnoAmigoError
from app.core.logging_config import get_logger

logger = get_logger(__name__)


def _error_body(message: str) -> dict:
    return {"detail": message}


def register_exception_handlers(app: FastAPI) -> None:

    @app.exception_handler(TecnoAmigoError)
    async def handle_domain_error(request: Request, exc: TecnoAmigoError) -> JSONResponse:
        log = getattr(logger, exc.log_level, logger.error)
        log(
            "[%s] %s %s → %s | interno: %s",
            exc.__class__.__name__,
            request.method,
            request.url.path,
            exc.message,
            exc.detail,
        )
        return JSONResponse(status_code=exc.http_status, content=_error_body(exc.message))

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.error(
            "[UnexpectedError] %s %s | %s: %s\n%s",
            request.method,
            request.url.path,
            exc.__class__.__name__,
            str(exc),
            traceback.format_exc(),
        )
        return JSONResponse(
            status_code=500,
            content=_error_body("Ocurrió un error inesperado. Por favor intenta nuevamente."),
        )
