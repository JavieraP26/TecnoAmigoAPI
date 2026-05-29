"""
Crea el primer administrador en la BD.

Uso:
    cd backend
    DATABASE_URL=postgresql+asyncpg://... SECRET_KEY=... python -m scripts.create_admin
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


async def main():
    from app.models.admin import AdminUser
    from app.services.admin_auth_service import hash_password

    email = input("Email de administrador: ").strip()
    if not email:
        print("Email requerido.")
        return

    import getpass
    password = getpass.getpass("Contraseña: ")
    if len(password) < 10:
        print("La contraseña debe tener al menos 10 caracteres.")
        return

    from app.config import settings
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
    from sqlalchemy import select

    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        existing = await db.execute(select(AdminUser).where(AdminUser.email == email))
        if existing.scalar_one_or_none():
            print(f"Ya existe un administrador con el email '{email}'.")
            await engine.dispose()
            return

        admin = AdminUser(email=email, password_hash=hash_password(password))
        db.add(admin)
        await db.commit()

    await engine.dispose()

    print(f"\nAdministrador '{email}' creado correctamente.")
    print("En el primer login recibirás el URI para configurar tu app de autenticación (TOTP).")


if __name__ == "__main__":
    asyncio.run(main())
