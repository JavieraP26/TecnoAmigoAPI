# TecnoAmigo

> Plataforma de inclusión digital para adultos mayores (65+) en Chile.  
> Sin fines de lucro. Basada en evidencia científica y diseño centrado en capacidades.

---

## Stack

### Backend
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge)

### Mobile
![React Native](https://img.shields.io/badge/React_Native-0.76-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Expo](https://img.shields.io/badge/Expo-SDK_56-000020?style=for-the-badge&logo=expo&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.6-007ACC?style=for-the-badge&logo=typescript&logoColor=white)

### Infraestructura
![Railway](https://img.shields.io/badge/Railway-Backend-0B0D0E?style=for-the-badge&logo=railway&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)
![Twilio](https://img.shields.io/badge/Twilio-SMS_OTP-F22F46?style=for-the-badge&logo=twilio&logoColor=white)

---

## El Problema

### Contexto Chile 2026

- **69.5%** de hogares sin conexión están encabezados por personas mayores de 60 años
- **34.9%** de adultos mayores no está conectado por falta de conocimientos digitales
- **Solo 36%** sabe hacer trámites digitales de forma autónoma
- **La población mayor crecerá al 33%** de Chile en 2050

**Fuente:** Estrategia Nacional de Inclusión Digital 2025-2035 (SENAMA, SUBTEL, SEGEGOB)

### El problema real no es de acceso

El 93% de los hogares chilenos tiene internet. La barrera es de **conocimiento, confianza y herramientas inadecuadas**.

Las soluciones actuales fallan porque:
- Asumen déficit por edad ("son lentos", "no entienden")
- Infantilizan interfaces en vez de amplificarlas
- Usan pedagogía tradicional en lugar de andragogía
- No personalizan según la heterogeneidad real de habilidades
- Son asistencialistas e insostenibles

---

## La Solución

### Academia de Simuladores sin riesgo

Réplicas funcionales de apps reales en un ambiente completamente seguro:
- **WhatsApp** — enviar mensajes, fotos, audios a contactos ficticios
- **BancoEstado** — consultar saldo, transferir, pagar cuentas (sin dinero real)
- **ClaveÚnica** — hacer trámites del Estado paso a paso

Sin dinero real, sin documentos reales, sin conexión externa. Cualquier error se deshace.

### Metodología basada en evidencia

**Andragogía** (Knowles): autonomía, experiencia previa, relevancia práctica inmediata.  
**Heutagogía** (Hase & Kenyon): autodirección, rutas personalizadas, sin presión.

### Diseño centrado en capacidades, no en edad

- Contraste mínimo 4.5:1, touch targets ≥ 48px, tipografía ≥ 16px
- Consistencia de ubicación (WCAG 2.2)
- Sin lenguaje de "racha" ni presión — solo celebración de logros

---

## Arquitectura

```
backend/          FastAPI + SQLAlchemy async + Alembic
├── app/
│   ├── routers/  11 módulos de endpoints
│   ├── services/ 13 capas de lógica de negocio
│   ├── models/   ORM SQLAlchemy
│   ├── schemas/  Pydantic v2
│   └── core/     seguridad, rate limiting, dependencias
├── alembic/      migraciones versionadas
├── scripts/      seed data, create_admin
└── tests/        99 tests async (pytest + httpx)

mobile/           React Native + Expo SDK 56
├── app/          Expo Router (file-based routing)
│   ├── (auth)/   splash, onboarding, registro, verificación OTP
│   └── (app)/    tabs: inicio, academia, ayuda, perfil
├── components/   ui/ y layout/ — responsabilidad única por archivo
├── contexts/     AuthContext con JWT + refresh automático
├── lib/          api.ts (axios + interceptores), storage.ts
└── constants/    colores, tipografía, espaciado
```

---

## Estado del proyecto

| Módulo | Estado |
|--------|--------|
| Backend completo (auth, lecciones, logros, simuladores, admin) | ✅ |
| 99 tests async pasando | ✅ |
| Despliegue Railway + Supabase | ✅ |
| Design system móvil (colores, Lexend, spacing) | ✅ |
| Componentes base (Button, Card, Input, ProgressBar, etc.) | ✅ |
| Flujo auth móvil (onboarding → registro → OTP) | ✅ |
| Tabs de navegación | ✅ (placeholders) |
| Dashboard, academia, simuladores, logros, perfil | ⏳ En desarrollo |
| Build Android (EAS) | ⏳ Pendiente |

---

## Ejecución local

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # completar variables
alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload
```

### Tests

```bash
cd backend
pytest -v
```

### Mobile

```bash
cd mobile
npm install
npx expo start
```

Requiere la variable `EXPO_PUBLIC_API_URL` apuntando al backend.

---

## Variables de entorno

Ver `backend/.env.example` para el listado completo.  
Variables críticas: `DATABASE_URL`, `SECRET_KEY`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `ALLOWED_ORIGINS`.

---

## Referencias

- Knowles, M. S. (2006). *The Adult Learner*. Elsevier.
- Hase, S., & Kenyon, C. (2000). From andragogy to heutagogy. *Ultibase*, 5(3).
- W3C (2024). *Web Content Accessibility Guidelines (WCAG) 2.2*.
- Cardozo, C. et al. (2018). Recomendaciones de Diseño para Usuarios Adultos Mayores en Interfaces Móviles.
- SENAMA & SEGEGOB (2025). *Estrategia Nacional de Inclusión Digital 2025-2035*.

---

## Licencia

Apache 2.0 — ver [LICENSE](LICENSE).

Hecho con compromiso por la inclusión digital en Chile.
