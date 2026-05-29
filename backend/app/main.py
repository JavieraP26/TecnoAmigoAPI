from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging_config import setup_logging
from app.core.error_handlers import register_exception_handlers
from app.routers import auth, lessons, progress, assessment

setup_logging()

app = FastAPI(
    title="TecnoAmigo API",
    description="Plataforma de inclusión digital para adultos mayores en Chile.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(auth.router)
app.include_router(lessons.router)
app.include_router(progress.router)
app.include_router(assessment.router)


@app.get("/health", tags=["sistema"])
async def health():
    return {"status": "ok"}
