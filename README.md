# TecnoAmigo 🤝

> Plataforma de inclusión digital para adultos mayores en Chile, basada en evidencia científica y diseño centrado en capacidades.

## Stack Tecnológico

### Backend
![Spring Boot](https://img.shields.io/badge/Spring_Boot-4.0.1-6DB33F?style=for-the-badge&logo=spring-boot&logoColor=white)
![Java](https://img.shields.io/badge/Java-21-ED8B00?style=for-the-badge&logo=openjdk&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![Flyway](https://img.shields.io/badge/Flyway-10.20-CC0200?style=for-the-badge&logo=flyway&logoColor=white)

### Frontend
![React](https://img.shields.io/badge/React-18.3-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=for-the-badge&logo=next.js&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.6-007ACC?style=for-the-badge&logo=typescript&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind_CSS-4.0-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)

### Tools
![Docker](https://img.shields.io/badge/Docker-27.4-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Maven](https://img.shields.io/badge/Maven-3.9-C71A36?style=for-the-badge&logo=apache-maven&logoColor=white)
![Swagger](https://img.shields.io/badge/Swagger-2.3-85EA2D?style=for-the-badge&logo=swagger&logoColor=black)
![JWT](https://img.shields.io/badge/JWT-0.12.5-000000?style=for-the-badge&logo=json-web-tokens&logoColor=white)

---

## 📋 Índice

- [El Problema](#-el-problema)
- [Nuestra Solución](#-nuestra-solución)
- [Diferenciadores Clave](#-diferenciadores-clave)
- [Arquitectura Técnica](#%EF%B8%8F-arquitectura-técnica)
- [Impacto Social y Económico](#-impacto-social-y-económico)


---

## 🚨 El Problema

### Contexto Chile 2026

- **69.5%** de hogares sin conexión están encabezados por personas mayores de 60 años
- **34.9%** de adultos mayores no está conectado por falta de conocimientos digitales
- **Solo 36%** sabe hacer trámites digitales de forma autónoma
- **La población mayor crecerá a 33%** de Chile en 2050

**Fuente:** [Estrategia Nacional de Inclusión Digital 2025-2035](https://www.senama.gob.cl), SUBTEL-SEGEGOB-SENAMA (julio 2025)

### El Verdadero Problema No Es Técnico

La exclusión digital de personas mayores **no es una brecha de acceso** (93% de hogares tiene internet), sino una **barrera de conocimiento, confianza y herramientas inadecuadas**.

Las soluciones actuales fallan porque:
- ❌ Asumen déficit por edad ("son lentos", "no entienden")
- ❌ Infantilizan interfaces (simplificación excesiva)
- ❌ Usan pedagogía tradicional (no andragogía)
- ❌ No personalizan por heterogeneidad de habilidades
- ❌ Son asistencialistas (insostenibles)

---

## 💡 Nuestra Solución

**TecnoAmigo** es una plataforma integral de aprendizaje digital que combina:

### 1️⃣ Diseño Centrado en Capacidades (No en Edad)

- **Interfaces adaptativas dinámicas** basadas en desempeño real, no asunciones
- **Contraste 4.5:1 mínimo**, touch targets 48px, tipografía ≥16px
- **Consistencia de ubicación** (WCAG 2.2 Criterio 3.2.6): botones siempre en misma posición

### 2️⃣ Academia de Simuladores Sin Riesgo

Réplicas funcionales de apps reales (WhatsApp, BancoEstado, ClaveÚnica) en ambiente seguro:
- ✅ **Sin dinero real**, sin documentos reales, sin conexión externa
- ✅ **Reversibilidad total**: cualquier error se deshace
- ✅ **Microlearning**: lecciones de 3-5 minutos respetando fatiga cognitiva

### 3️⃣ Metodología Educativa Basada en Evidencia

**Andragogía** (Knowles, 2006):
- Autonomía del estudiante
- Aprendizaje basado en experiencia previa
- Relevancia práctica inmediata

**Heutagogía** (Hase & Kenyon, 2000):
- Autodirección con IA personalizada
- Recomendaciones dinámicas por desempeño
- Rutas de aprendizaje individualizadas

### 4️⃣ Modelo B2B/B2G Sostenible

- Licencias municipales (CLP 15-25M/año)
- Patrocinios bancarios (CLP 50-80M/año)
- Alianzas estratégicas: SENAMA, Entel, CCAF

---

## 🎯 Diferenciadores Clave

| Solución Tradicional | TecnoAmigo |
|---------------------|------------|
| Tutorial teórico de WhatsApp | Simulador funcional donde envías mensaje real a "tu hija" |
| "Los mayores no entienden" | Heterogeneidad reconocida: cada usuario es único |
| Simplificación condescendiente | Amplificación respetuosa (más grande, no más tonto) |
| Talleres presenciales no escalables | Plataforma digital + soporte híbrido |
| Sin datos de progreso | IA que adapta interfaz cada 24h según errores/aciertos |

---

## 🏗️ Arquitectura Técnica

### Backend (Spring Boot 4.0.1 + Java 21)

**Principios arquitectónicos:**
- ✅ **Clean Architecture** (Hexagonal): dominio independiente de frameworks
- ✅ **SOLID**: separación de responsabilidades
- ✅ **DDD**: agregados, value objects, repositorios
- ✅ **Flyway**: migraciones versionadas de base de datos
- ✅ **OpenAPI/Swagger**: documentación automática de API

### Frontend (React/Next.js)


**Stack frontend:**
- **React 18** con TypeScript
- **Next.js 14** (App Router) para SSR/SEO
- **Tailwind CSS** con presets age-friendly
- **Framer Motion** para animaciones sutiles
- **React Query** para cache de API

### Base de Datos (PostgreSQL 15)

- Esquema relacional normalizado
- Índices en columnas de búsqueda frecuente
- Backups automáticos diarios
- Replicación para alta disponibilidad


### IA para personalización

- Modelos de recomendación basados en desempeño
- Análisis de patrones de error para adaptar interfaz

## Impacto Social Medible

- Dignidad y autonomía para adultos mayores
- Reducción de la brecha digital en Chile
- Escalabilidad nacional con enfoque sostenible
- Salud mental y bienestar social

## Impacto Económico

- Reducción de costos en asistencia presencial
- Mayor inclusión financiera y digital
- Potencial de mercado en licencias B2B/B2G

## 📚 Referencias Científicas
- Knowles, M. S. (2006). The Adult Learner. Elsevier.
- Hase, S., & Kenyon, C. (2000). From andragogy to heutagogy. Ultibase, 5(3), 1-10.
- W3C (2024). Web Content Accessibility Guidelines (WCAG) 2.2.
- Cardozo, C. et al. (2018). Recomendaciones de Diseño para Usuarios Adultos Mayores en Interfaces Móviles.
- SENAMA & SEGEGOB (2025). Estrategia Nacional de Inclusión Digital 2025-2035.

## 📄 Licencia
Este proyecto está bajo la Licencia Apache 2.0. Consulte el archivo [LICENSE](LICENSE) para más detalles.

Hecho con ❤️ y compromiso con la inclusión digital.

---