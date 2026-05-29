from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.core.limiter import limiter
from app.core.logging_config import setup_logging
from app.core.error_handlers import register_exception_handlers
from app.routers import (
    auth, lessons, progress, assessment, users,
    achievements, requests, simulators, journey,
    admin_auth, admin,
)

setup_logging()

app = FastAPI(
    title="TecnoAmigo API",
    description="Plataforma de inclusión digital para adultos mayores en Chile.",
    version="0.1.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(lessons.router)
app.include_router(progress.router)
app.include_router(assessment.router)
app.include_router(achievements.router)
app.include_router(requests.router)
app.include_router(simulators.router)
app.include_router(journey.router)
app.include_router(admin_auth.router)
app.include_router(admin.router)


@app.get("/health", tags=["sistema"])
async def health():
    from sqlalchemy import text
    from app.database import AsyncSessionLocal
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "ok"}
    except Exception:
        return {"status": "ok", "db": "unreachable"}
