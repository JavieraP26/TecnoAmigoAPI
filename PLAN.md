# Plan de Implementación — TecnoAmigo

> Plataforma de inclusión digital para adultos mayores (65+) en Chile.  
> Estado actual: backend completo (99 tests), frontend Fase 1 terminada.

---

## Índice

1. [Estado actual del proyecto](#1-estado-actual)
2. [Arquitectura general](#2-arquitectura)
3. [Backend — trabajo pendiente](#3-backend)
4. [Frontend móvil — fases por pantalla](#4-frontend-movil)
5. [Configuraciones externas](#5-configuraciones-externas)
6. [Tests — cobertura actual y pendiente](#6-tests)
7. [Build y distribución Android](#7-build-android)
8. [Hoja de ruta futura](#8-roadmap-futuro)
9. [Convención de commits](#9-convención-de-commits)

---

## 1. Estado actual

### Backend (`/backend`) — ✅ Listo para producción

| Área | Estado |
|------|--------|
| Auth SMS OTP + JWT + refresh rotation | ✅ |
| Admin portal (TOTP MFA) | ✅ |
| Usuarios, perfil, preferencias | ✅ |
| Evaluación inicial (assessment) | ✅ |
| Catálogo de lecciones | ✅ |
| Progreso y reproductor | ✅ |
| Logros (14 achievements) | ✅ |
| Simuladores (5 seed) | ✅ |
| Peticiones de la comunidad + votos | ✅ |
| Jornada / graduación | ✅ |
| PDF resumen personal | ✅ |
| Rate limiting (slowapi) | ✅ |
| Migraciones Alembic (2) | ✅ |
| Seed data (logros + simuladores) | ✅ |
| Despliegue Railway + Supabase | ✅ |
| 99 tests async (pytest + httpx) | ✅ |

### Frontend móvil (`/mobile`) — 🔄 En progreso

| Área | Estado |
|------|--------|
| Design system (colores, tipografía, spacing) | ✅ Fase 1 |
| Componentes UI (Button, Card, Input, etc.) | ✅ Fase 1 |
| AuthContext + api.ts (JWT + refresh) | ✅ Fase 1 |
| Expo Router root layout + fonts | ✅ Fase 1 |
| Splash + Onboarding + Registro + OTP | ✅ Fase 1 |
| Tabs (Inicio, Academia, Ayuda, Perfil) | ✅ Fase 1 (placeholders) |
| Evaluación inicial | ⏳ Fase 2 |
| Dashboard + bienvenida contextual | ⏳ Fase 2 |
| Catálogo Academia | ⏳ Fase 3 |
| Reproductor de lección | ⏳ Fase 3 |
| Simuladores interactivos | ⏳ Fase 4 |
| Centro de logros | ⏳ Fase 5 |
| Peticiones comunidad | ⏳ Fase 5 |
| Jornada / graduación | ⏳ Fase 5 |
| Perfil + edición | ⏳ Fase 6 |
| Ajustes de accesibilidad | ⏳ Fase 6 |
| EAS Build + distribución APK | ⏳ Fase 7 |

---

## 2. Arquitectura

```
TecnoAmigoAPI/
├── backend/         FastAPI + SQLAlchemy + asyncpg
│   ├── app/
│   │   ├── routers/   (11 módulos de endpoints)
│   │   ├── services/  (13 capas de lógica)
│   │   ├── models/    (SQLAlchemy ORM)
│   │   ├── schemas/   (Pydantic v2)
│   │   └── core/      (seguridad, deps, rate limit)
│   ├── alembic/       (migraciones)
│   ├── scripts/       (seed, create_admin)
│   └── tests/         (99 tests async)
│
├── mobile/          React Native + Expo SDK 56
│   ├── app/         (Expo Router — file-based routing)
│   │   ├── (auth)/  (splash, onboarding, register, verify)
│   │   └── (app)/   (tabs: index, academy, simulators, profile)
│   ├── components/  (ui/, layout/)
│   ├── contexts/    (AuthContext)
│   ├── lib/         (api.ts, storage.ts)
│   ├── constants/   (colors, typography, spacing)
│   └── hooks/
│
└── frontend/        Prototipos HTML (referencia de diseño)
```

**Servicios externos:**
- **Supabase** — PostgreSQL con Transaction Pooler (puerto 6543)
- **Railway** — hosting backend (autoescala, CI via `railway.toml`)
- **Twilio** — SMS OTP
- **EAS (Expo Application Services)** — builds nativos Android/iOS
- **Sentry** *(pendiente)* — error tracking en producción

---

## 3. Backend — trabajo pendiente

El backend está listo, pero hay pulish de producción por hacer:

### 3a. Seguridad y hardening
- [ ] Agregar header `X-Request-ID` en cada respuesta (trazabilidad de logs)
- [ ] Validar que `ENVIRONMENT=production` bloquee `/docs` y `/redoc`
- [ ] Revisar que todos los endpoints de admin devuelvan 404 (no 401) cuando `ENVIRONMENT=production` y el request no tiene token, para no revelar que la ruta existe

### 3b. Monitoreo
- [ ] Integrar Sentry SDK: `pip install sentry-sdk[fastapi]`
- [ ] Configurar `SENTRY_DSN` en Railway variables
- [ ] Log estructurado en JSON (ya existe `logging_config.py`, verificar formato)

### 3c. Migración futura — si la app crece
- `0003_add_push_tokens.py` — tabla para Expo Push Notifications
- `0004_add_notifications.py` — historial de notificaciones por usuario

### 3d. Endpoints aún no implementados (nice-to-have)
- `GET /users/me/export` — exportar datos personales (GDPR-style)
- `POST /auth/deactivate` — que el usuario pueda borrar su cuenta
- `GET /admin/analytics/retention` — retención a 7/30 días

---

## 4. Frontend móvil — fases por pantalla

> **Regla de oro:** un commit = una pantalla o un grupo cohesionado de componentes  
> Máximo ~150 líneas por archivo de pantalla. Extraer lógica a hooks si supera eso.

---

### Fase 2 — Evaluación inicial + Dashboard

#### 2.1 — Hook `useWelcome`
Archivo: `hooks/useWelcome.ts`  
Responsabilidad: fetch a `/progress/welcome`, devuelve `{ returning, daysSince, totalActiveDays }`.  
**Commit:** `feat(mobile): hook useWelcome para contexto de bienvenida`

#### 2.2 — Hook `useJourney`
Archivo: `hooks/useJourney.ts`  
Responsabilidad: fetch a `/journey/status`, devuelve estado de progreso y logros.  
**Commit:** `feat(mobile): hook useJourney para estado de jornada`

#### 2.3 — Pantalla de evaluación inicial
Archivo: `app/(auth)/assessment.tsx`  
Prototipo: `frontend/evaluación_inicial/`  
Responsabilidad: wizard de 5-7 preguntas (área + nivel), POST a `/assessment/submit`, redirige a `/(app)`.  
Extraer: `components/ui/QuestionCard.tsx` (tarjeta de opción de respuesta, 56px touch target).  
**Commit:** `feat(mobile): QuestionCard — componente de respuesta de evaluación`  
**Commit:** `feat(mobile): pantalla de evaluación inicial`

#### 2.4 — Componente `WelcomeBanner`
Archivo: `components/dashboard/WelcomeBanner.tsx`  
Responsabilidad: saludo contextual según `returning` y `daysSince`. Sin presión, solo calidez.  
Casos:
- Primera vez: "¡Bienvenida, Rosa! Empecemos juntos."
- Regresó hoy: "¡Hola de nuevo!"
- Regresó después de N días: "¡Qué bueno verte! Han pasado N días."  
**Commit:** `feat(mobile): WelcomeBanner — saludo contextual en dashboard`

#### 2.5 — Componente `CurrentLessonCard`
Archivo: `components/dashboard/CurrentLessonCard.tsx`  
Responsabilidad: mostrar lección en curso con barra de progreso y botón Continuar.  
**Commit:** `feat(mobile): CurrentLessonCard — tarjeta de lección en curso`

#### 2.6 — Componente `SimulatorsGrid`
Archivo: `components/dashboard/SimulatorsGrid.tsx`  
Responsabilidad: grilla 2x2 de accesos rápidos a simuladores.  
**Commit:** `feat(mobile): SimulatorsGrid — acceso rápido a simuladores`

#### 2.7 — Componente `AchievementsSummary`
Archivo: `components/dashboard/AchievementsSummary.tsx`  
Responsabilidad: mini-resumen de logros (N desbloqueados / total).  
**Commit:** `feat(mobile): AchievementsSummary — resumen de logros en dashboard`

#### 2.8 — Dashboard completo (composición)
Archivo: `app/(app)/index.tsx` — refactorizar para usar los componentes anteriores.  
**Commit:** `feat(mobile): dashboard principal — composición de componentes`

---

### Fase 3 — Academia

#### 3.1 — Hook `useAcademy`
Archivo: `hooks/useAcademy.ts`  
Responsabilidad: fetch a `/lessons` con filtros de área y nivel.  
**Commit:** `feat(mobile): hook useAcademy para catálogo de lecciones`

#### 3.2 — Componente `LessonCard`
Archivo: `components/academy/LessonCard.tsx`  
Responsabilidad: tarjeta de lección con thumbnail, título, duración, barra de progreso.  
**Commit:** `feat(mobile): LessonCard — tarjeta de lección en catálogo`

#### 3.3 — Componente `AreaFilter`
Archivo: `components/academy/AreaFilter.tsx`  
Responsabilidad: chips horizontales para filtrar por área (WhatsApp, Banco, Trámites, etc.).  
**Commit:** `feat(mobile): AreaFilter — chips de filtro por área`

#### 3.4 — Pantalla catálogo Academia
Archivo: `app/(app)/academy.tsx`  
Prototipo: `frontend/catálogo_de_academia/`  
**Commit:** `feat(mobile): pantalla catálogo Academia`

#### 3.5 — Pantalla reproductor de lección
Archivo: `app/(app)/lesson/[id].tsx`  
Prototipo: `frontend/reproductor_de_lección/`  
Responsabilidad: navegación por pasos, texto grande, imágenes, botón "Siguiente" prominente (56px).  
Extraer: `components/lesson/StepIndicator.tsx`, `components/lesson/LessonStep.tsx`.  
**Commit:** `feat(mobile): StepIndicator + LessonStep — componentes del reproductor`  
**Commit:** `feat(mobile): pantalla reproductor de lección`

---

### Fase 4 — Simuladores

> Los simuladores son la joya de la plataforma: réplicas interactivas y seguras de apps reales.

#### 4.1 — Pantalla hub de simuladores
Archivo: `app/(app)/simulators.tsx`  
Responsabilidad: lista de simuladores disponibles (GET `/simulators`), cada uno con descripción y botón de inicio.  
**Commit:** `feat(mobile): pantalla hub de simuladores`

#### 4.2 — Simulador WhatsApp
Archivo: `app/(app)/simulator/whatsapp.tsx`  
Prototipo: `frontend/simulador_de_whatsapp/`  
Responsabilidad: interfaz idéntica a WhatsApp pero con datos ficticios. Pasos guiados con overlay de instrucciones. GET `/simulators/whatsapp/steps`.  
Extraer: `components/simulator/SimulatorOverlay.tsx` (capa de instrucciones encima de la UI).  
**Commit:** `feat(mobile): SimulatorOverlay — overlay de instrucciones para simuladores`  
**Commit:** `feat(mobile): simulador WhatsApp`

#### 4.3 — Simulador BancoEstado
Archivo: `app/(app)/simulator/bancoestado.tsx`  
Prototipo: `frontend/simulador_bancoestado_2026/`  
**Commit:** `feat(mobile): simulador BancoEstado`

#### 4.4 — Simulador ClaveÚnica
Archivo: `app/(app)/simulator/claveunica.tsx`  
Prototipo: `frontend/landing_claveúnica_2026/`  
**Commit:** `feat(mobile): simulador ClaveÚnica`

---

### Fase 5 — Logros, comunidad y jornada

#### 5.1 — Hook `useAchievements`
Archivo: `hooks/useAchievements.ts`  
**Commit:** `feat(mobile): hook useAchievements`

#### 5.2 — Componente `AchievementBadge`
Archivo: `components/achievements/AchievementBadge.tsx`  
Responsabilidad: insignia de logro (bloqueada/desbloqueada), 72x72px.  
**Commit:** `feat(mobile): AchievementBadge — insignia de logro`

#### 5.3 — Pantalla centro de logros
Archivo: `app/(app)/achievements.tsx`  
Prototipo: `frontend/centro_de_logros_rosa/`  
Responsabilidad: grilla de logros, filtro bloqueados/desbloqueados.  
**Commit:** `feat(mobile): pantalla centro de logros`

#### 5.4 — Modal celebración de logro nuevo
Archivo: `components/achievements/AchievementCelebration.tsx`  
Prototipo: `frontend/celebración_logro_nuevo/`  
Responsabilidad: modal/sheet con animación cuando se desbloquea un logro.  
**Commit:** `feat(mobile): AchievementCelebration — modal de celebración de logro`

#### 5.5 — Pantalla peticiones de la comunidad
Archivo: `app/(app)/requests.tsx`  
Responsabilidad: listado de temas pedidos por la comunidad. Botón para votar. Indicador de `pending_voted_requests`.  
**Commit:** `feat(mobile): pantalla peticiones de la comunidad`

#### 5.6 — Pantalla jornada y graduación
Archivo: `app/(app)/journey.tsx`  
Responsabilidad: progreso general, indicador `ready_to_graduate`, botón de graduación (libre elección del usuario).  
**Commit:** `feat(mobile): pantalla jornada y graduación`

---

### Fase 6 — Perfil y accesibilidad

#### 6.1 — Componente `UserActivityCard`
Archivo: `components/profile/UserActivityCard.tsx`  
Responsabilidad: "días de aprendizaje" — sin racha/presión, solo calor y celebración de constancia.  
Prototipo: `frontend/detalle_de_mi_racha/` (adaptar copy, remover lenguaje de presión).  
**Commit:** `feat(mobile): UserActivityCard — días de aprendizaje sin presión`

#### 6.2 — Pantalla perfil de usuario
Archivo: `app/(app)/profile.tsx`  
Prototipo: `frontend/perfil_de_usuario/`  
Responsabilidad: foto, nombre, ciudad, días activos, botón editar.  
**Commit:** `feat(mobile): pantalla perfil de usuario`

#### 6.3 — Pantalla editar perfil
Archivo: `app/(app)/profile-edit.tsx`  
Prototipo: `frontend/editar_perfil_senior/`  
Responsabilidad: nombre, ciudad, duración preferida de lección. PATCH `/users/me`.  
**Commit:** `feat(mobile): pantalla editar perfil`

#### 6.4 — Ajustes de accesibilidad
Archivo: `app/(app)/settings.tsx`  
Responsabilidad: tamaño de fuente (pequeño / normal / grande), contraste (por ahora solo preparar la estructura, aplicar en Fase 7).  
**Commit:** `feat(mobile): pantalla ajustes de accesibilidad`

---

### Fase 7 — Build, deploy y pulish final

#### 7.1 — Variables de entorno móviles
Archivo: `mobile/.env.local` (no commiteado), `mobile/.env.example` (commiteado).  
Variables: `EXPO_PUBLIC_API_URL`, `EXPO_PUBLIC_SENTRY_DSN`.  
**Commit:** `chore(mobile): .env.example con variables de entorno`

#### 7.2 — EAS Build para Android
Archivo: `mobile/eas.json`.  
Configurar profiles: `development` (APK debug), `preview` (APK release), `production` (AAB para Play Store).  
```json
{
  "build": {
    "development": { "android": { "buildType": "apk" } },
    "preview": { "android": { "buildType": "apk" }, "distribution": "internal" },
    "production": { "android": { "buildType": "app-bundle" } }
  }
}
```
**Commit:** `chore(mobile): configuración EAS Build`

#### 7.3 — Sentry en móvil
`npx expo install @sentry/react-native`  
Integrar en `app/_layout.tsx`, configurar DSN.  
**Commit:** `feat(mobile): integración Sentry para error tracking`

#### 7.4 — Pruebas de accesibilidad manuales
Checklist antes del primer APK:
- [ ] Todos los touch targets ≥ 48px
- [ ] Fuente ≥ 16px en cuerpo, ≥ 18px en botones
- [ ] Contraste ≥ 4.5:1 (texto sobre fondo)
- [ ] TalkBack (Android) puede navegar todas las pantallas
- [ ] Sin animaciones que no se puedan desactivar

---

## 5. Configuraciones externas

### Railway (backend)
```toml
# railway.toml — ya configurado
[deploy]
startCommand = "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
```
Variables de entorno necesarias en Railway:
```
DATABASE_URL=postgresql+asyncpg://...  # Supabase Transaction Pooler puerto 6543
SECRET_KEY=<256-bit random>
REFRESH_SECRET_KEY=<256-bit random>
ADMIN_SECRET_KEY=<256-bit random>
PRE_AUTH_SECRET_KEY=<256-bit random>
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...
ALLOWED_ORIGINS=https://tecnoamigo.cl,https://admin.tecnoamigo.cl
ENVIRONMENT=production
SENTRY_DSN=...  (pendiente)
```

### Supabase
- Pool mode: **Transaction** (PgBouncer), puerto 6543
- `connect_args={"prepared_statement_cache_size": 0}` — ya configurado en `database.py`
- Activar **Row Level Security** en tablas de usuarios si algún día Supabase se usa directo desde el móvil
- Backup automático: habilitado por defecto en Supabase (7 días tier gratuito)

### Twilio
- Número de origen: uno con capacidad SMS para Chile (+56)
- Verificar que la cuenta esté aprobada para enviar a Chile (puede requerir registro A2P)
- Límite en `send-sms`: 3/10min ya implementado en backend

### EAS (Expo Application Services)
```bash
npm install -g eas-cli
eas login
eas build:configure   # genera eas.json
eas build --profile preview --platform android   # primer APK
```
- Requiere cuenta Expo (gratuita para uso básico)
- Para distribución interna: `eas submit` o link directo al APK

### Sentry (pendiente — recomendado antes del primer usuario real)
```bash
# Backend
pip install sentry-sdk[fastapi]

# Mobile
npx expo install @sentry/react-native
```
Configurar proyecto separado para backend y mobile en sentry.io (plan gratuito suficiente al inicio).

### Dominio (opcional pero recomendado)
- `api.tecnoamigo.cl` → Railway (CNAME)
- `tecnoamigo.cl` → landing page (puede ser un simple HTML en GitHub Pages por ahora)

---

## 6. Tests — cobertura actual y pendiente

### Backend — estado actual (99 tests ✅)

| Archivo | Tests | Cubre |
|---------|-------|-------|
| test_auth.py | ~12 | SMS OTP, JWT, refresh |
| test_users.py | ~10 | Perfil CRUD, validaciones |
| test_assessment.py | ~8 | Evaluación inicial |
| test_lessons.py | ~10 | Catálogo, reproductor |
| test_progress.py | ~8 | Progreso, welcome context |
| test_achievements.py | ~10 | Logros, desbloqueo |
| test_requests.py | ~8 | Peticiones, votos |
| test_simulators.py | ~8 | CRUD simuladores |
| test_journey.py | ~12 | Jornada, graduación |
| test_admin.py | ~9 | Panel admin |
| test_admin_auth.py | ~8 | TOTP MFA |

### Backend — tests pendientes

```
backend/tests/
├── test_pdf.py          # Generación de PDF resumen
├── test_rate_limits.py  # Verificar que el rate limit bloquea correctamente
├── test_sms_service.py  # Mock de Twilio (ya existe MockSmsService en conftest)
└── test_edge_cases.py   # Tokens expirados, usuarios duplicados, etc.
```

Test específicos que faltan:
- `test_refresh_token_rotation` — verificar que el refresh viejo queda revocado
- `test_concurrent_refresh` — dos requests simultáneos con el mismo refresh token
- `test_graduated_user_cant_graduate_again` — idempotencia de graduación
- `test_pdf_generates_correctly` — smoke test de fpdf2

### Frontend móvil — tests (pendiente, Fase 7)

Stack recomendado: **Jest + @testing-library/react-native + Maestro (E2E)**

```bash
npm install --save-dev jest @testing-library/react-native jest-expo
```

```
mobile/
├── __tests__/
│   ├── components/
│   │   ├── Button.test.tsx        # renders, disabled, loading
│   │   ├── TextInput.test.tsx     # focus, error state
│   │   ├── ProgressBar.test.tsx   # clamp 0-1
│   │   └── WelcomeBanner.test.tsx # casos: primera vez, returning, días
│   ├── hooks/
│   │   ├── useWelcome.test.ts     # mock api, estados loading/error
│   │   └── useJourney.test.ts
│   └── screens/
│       ├── register.test.tsx      # validación +56, 9 dígitos
│       └── verify.test.tsx        # OTP, countdown, reenvío
```

E2E con Maestro (más simple que Detox, no requiere Xcode/Gradle corriendo):
```yaml
# .maestro/flows/auth_flow.yaml
appId: cl.tecnoamigo.app
---
- launchApp
- assertVisible: "Bienvenido a TecnoAmigo"
- tapOn: "Comenzar"
- tapOn: "Enviar código SMS"
- assertVisible: "Ingresa el código"
```

---

## 7. Build y distribución Android

### Flujo de versiones

```
develop (feature branches)
    ↓ PR + review
main
    ↓ tag v1.x.x
EAS Build (preview APK)
    ↓ QA manual en dispositivo físico Samsung/LG (65+)
EAS Build (production AAB)
    ↓
Google Play Store (alpha → beta → producción)
```

### Checklist pre-release

- [ ] `app.json` version bumpeado
- [ ] `eas.json` configurado con todos los profiles
- [ ] Variables de entorno en EAS Secrets
- [ ] Prueba en dispositivo físico Android 10+ (no solo emulador)
- [ ] TalkBack habilitado — navegar toda la app
- [ ] Sin crashlytics/Sentry no configurado (errores silenciosos = mala experiencia)
- [ ] APK instalado en al menos un Samsung Galaxy A (el más común en adultos mayores Chile)

---

## 8. Roadmap futuro

### V1.1 — Notificaciones push
- Expo Push Notifications + tabla `push_tokens` (migración 0003)
- Notificar cuando una petición votada queda disponible
- Recordatorio suave (una vez por semana, miércoles 10am) si el usuario no ha entrado

### V1.2 — Modo offline básico
- Cachear el contenido de la lección actual con AsyncStorage
- Mostrar banner "Sin conexión — estás viendo tu última lección guardada"

### V1.3 — Admin web dashboard
- Next.js 14 + App Router + shadcn/ui
- Rutas: /admin/users, /admin/requests, /admin/simulators, /admin/stats
- Autenticación: TOTP MFA ya implementado en backend

### V1.4 — iOS
- EAS Build para iOS requiere cuenta Apple Developer (99 USD/año)
- Misma codebase React Native, testear especialmente gestos y SafeArea en iPhone

### V1.5 — ClaveÚnica OAuth real
- El simulador actual es educativo; la integración real requiere convenio con el gobierno (api.claveunica.gob.cl)
- Contactar SEGPRES para registro como entidad integradora

### V2.0 — Módulos comunitarios
- Grupos por ciudad (Santiago, Valparaíso, Concepción)
- Mentor peer-to-peer: usuario avanzado puede ayudar a uno nuevo
- Certificado de participación (ya existe el PDF de logros, extender a certificado formal)

---

## 9. Convención de commits

### Regla principal: un commit = una responsabilidad

❌ Mal:
```
feat(mobile): fase 2 completa - assessment, dashboard, hooks, componentes
```

✅ Bien:
```
feat(mobile): hook useWelcome para contexto de bienvenida
feat(mobile): WelcomeBanner — saludo contextual
feat(mobile): CurrentLessonCard — lección en curso
feat(mobile): dashboard principal — composición
```

### Prefijos

| Prefijo | Cuándo usarlo |
|---------|---------------|
| `feat(mobile):` | Nueva pantalla o componente visible |
| `feat(backend):` | Nuevo endpoint o servicio |
| `fix(mobile):` | Bug en pantalla/componente |
| `fix(backend):` | Bug en lógica o test |
| `chore(mobile):` | Config, deps, archivos no funcionales |
| `chore(backend):` | Igual |
| `test(backend):` | Nuevo test o corrección de test |
| `style(mobile):` | Solo cambios visuales sin lógica |
| `refactor(mobile):` | Restructurar sin cambiar comportamiento |

### Tamaño máximo de archivos de pantalla

- **Pantallas** (`app/.../screen.tsx`): ≤ 150 líneas. Si supera, extraer lógica a hook o componente.
- **Componentes** (`components/.../Component.tsx`): ≤ 100 líneas.
- **Hooks** (`hooks/useXxx.ts`): ≤ 60 líneas.

Si un archivo crece más, es señal de que tiene más de una responsabilidad.
