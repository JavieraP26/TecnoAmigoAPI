"""
Seed inicial de la base de datos.

Inserta los logros base y el catálogo inicial de simuladores.
Diseñado para ser idempotente: si los registros ya existen, los omite.

Uso:
    cd backend
    DATABASE_URL=postgresql+asyncpg://... python -m scripts.seed
"""
import asyncio
import os
import sys

# Permite ejecutar desde backend/ sin instalar el paquete
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

from app.models.achievement import Achievement, TriggerType
from app.models.content import SimulatorCatalog, ModuleType, ContentArea


# ---------------------------------------------------------------------------
# Logros iniciales (13 keys)
# El frontend mapea cada key a título, descripción e ícono en el idioma que quiera.
# ---------------------------------------------------------------------------

ACHIEVEMENTS = [
    # --- Por cantidad de lecciones completadas ---
    {
        "key": "primera_leccion",
        "trigger_type": TriggerType.lesson_count,
        "content_area": None,
        "threshold": 1,
    },
    {
        "key": "cinco_lecciones",
        "trigger_type": TriggerType.lesson_count,
        "content_area": None,
        "threshold": 5,
    },
    {
        "key": "diez_lecciones",
        "trigger_type": TriggerType.lesson_count,
        "content_area": None,
        "threshold": 10,
    },
    # --- Primera lección de cada área (desbloqueo de área) ---
    {
        "key": "explora_comunicacion",
        "trigger_type": TriggerType.area_first,
        "content_area": ContentArea.comunicacion.value,
        "threshold": 1,
    },
    {
        "key": "explora_banca",
        "trigger_type": TriggerType.area_first,
        "content_area": ContentArea.banca.value,
        "threshold": 1,
    },
    {
        "key": "explora_seguridad",
        "trigger_type": TriggerType.area_first,
        "content_area": ContentArea.seguridad.value,
        "threshold": 1,
    },
    {
        "key": "explora_gobierno",
        "trigger_type": TriggerType.area_first,
        "content_area": ContentArea.gobierno.value,
        "threshold": 1,
    },
    {
        "key": "explora_mi_telefono",
        "trigger_type": TriggerType.area_first,
        "content_area": ContentArea.mi_telefono.value,
        "threshold": 1,
    },
    # --- Área completada (todas las lecciones de esa área) ---
    {
        "key": "domina_comunicacion",
        "trigger_type": TriggerType.area_complete,
        "content_area": ContentArea.comunicacion.value,
        "threshold": 1,
    },
    {
        "key": "domina_banca",
        "trigger_type": TriggerType.area_complete,
        "content_area": ContentArea.banca.value,
        "threshold": 1,
    },
    {
        "key": "domina_seguridad",
        "trigger_type": TriggerType.area_complete,
        "content_area": ContentArea.seguridad.value,
        "threshold": 1,
    },
    {
        "key": "domina_gobierno",
        "trigger_type": TriggerType.area_complete,
        "content_area": ContentArea.gobierno.value,
        "threshold": 1,
    },
    {
        "key": "domina_mi_telefono",
        "trigger_type": TriggerType.area_complete,
        "content_area": ContentArea.mi_telefono.value,
        "threshold": 1,
    },
    # --- Evaluación inicial completada ---
    {
        "key": "evaluacion_inicial",
        "trigger_type": TriggerType.assessment_complete,
        "content_area": None,
        "threshold": 1,
    },
]


# ---------------------------------------------------------------------------
# Catálogo inicial de simuladores
# ---------------------------------------------------------------------------

SIMULATORS = [
    {
        "slug": "whatsapp",
        "title": "WhatsApp",
        "description": "Aprende a enviar mensajes, fotos y llamadas de voz con WhatsApp.",
        "module_type": ModuleType.simulator,
        "content_area": ContentArea.comunicacion,
        "icon": "whatsapp",
        "difficulty": 1,
    },
    {
        "slug": "video_llamada",
        "title": "Videollamada",
        "description": "Practica cómo hacer y recibir videollamadas con FaceTime o WhatsApp.",
        "module_type": ModuleType.simulator,
        "content_area": ContentArea.comunicacion,
        "icon": "video",
        "difficulty": 2,
    },
    {
        "slug": "bancoestado",
        "title": "BancoEstado",
        "description": "Practica cómo revisar tu saldo, transferir dinero y pagar cuentas.",
        "module_type": ModuleType.simulator,
        "content_area": ContentArea.banca,
        "icon": "bank",
        "difficulty": 2,
    },
    {
        "slug": "clave_unica",
        "title": "Clave Única",
        "description": "Aprende a obtener y usar tu Clave Única del Estado para trámites en línea.",
        "module_type": ModuleType.simulator,
        "content_area": ContentArea.gobierno,
        "icon": "key",
        "difficulty": 2,
    },
    {
        "slug": "fonasa",
        "title": "FONASA en línea",
        "description": "Practica cómo pedir hora médica y revisar tu cobertura en FONASA.",
        "module_type": ModuleType.simulator,
        "content_area": ContentArea.gobierno,
        "icon": "health",
        "difficulty": 2,
    },
]


# ---------------------------------------------------------------------------
# Lógica de seed
# ---------------------------------------------------------------------------

async def seed():
    from app.config import settings
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        # Logros
        inserted_achievements = 0
        for data in ACHIEVEMENTS:
            exists = await db.execute(
                select(Achievement).where(Achievement.key == data["key"])
            )
            if exists.scalar_one_or_none() is None:
                db.add(Achievement(**data))
                inserted_achievements += 1

        # Simuladores
        inserted_simulators = 0
        for data in SIMULATORS:
            exists = await db.execute(
                select(SimulatorCatalog).where(SimulatorCatalog.slug == data["slug"])
            )
            if exists.scalar_one_or_none() is None:
                db.add(SimulatorCatalog(**data))
                inserted_simulators += 1

        await db.commit()

    await engine.dispose()

    print(f"Seed completado:")
    print(f"  Logros insertados:     {inserted_achievements} / {len(ACHIEVEMENTS)}")
    print(f"  Simuladores insertados: {inserted_simulators} / {len(SIMULATORS)}")


if __name__ == "__main__":
    asyncio.run(seed())
