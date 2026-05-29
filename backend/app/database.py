from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# prepared_statement_cache_size=0 requerido para Supabase Transaction Pooler (PgBouncer)
_connect_args = (
    {"prepared_statement_cache_size": 0}
    if settings.database_url.startswith("postgresql")
    else {}
)
engine = create_async_engine(settings.database_url, echo=False, connect_args=_connect_args)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass
