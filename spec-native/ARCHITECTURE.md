# ARCHITECTURE.md

Describe la arquitectura actual del proyecto.

## Vision general

`ether-ocr` es un servicio de extraccion de texto que expone una API REST
para que agentes externos y pipelines RAG consuman texto UTF-8 limpio desde
documentos heterogeneos (PDFs con/sin capa de texto, imagenes, texto plano).

El sistema **no** inserta datos en ningun RAG — solo extrae, limpia y
devuelve texto. Un agente externo se encarga de la ingestion.

## Modulos principales

### Capa de dominio (extraccion y limpieza)

- **`ether_ocr.extractor`**: invoca `pdftotext -layout` para convertir PDFs
  con capa de texto a texto crudo.
- **`ether_ocr.ocr`**: motor OCR con Tesseract para PDFs escaneados e imagenes.
  Soporta `ocr_image()` y `ocr_pdf_scanned()` via `pdf2image` + Poppler.
- **`ether_ocr.pipeline`**: orquesta extraccion Poppler o OCR segun el tipo
  de entrada. Decide automaticamente si el PDF tiene capa de texto o
  requiere OCR.
- **`ether_ocr.cleaner`**: normaliza artefactos de layout PDF, numeracion
  de pagina, espacios repetidos y separadores de articulos/secciones.
- **`ether_ocr.validator`**: rechaza Markdown, HTML y caracteres de control.
- **`ether_ocr.preparer`**: orquesta entrada, limpieza, validacion y escritura.

### Capa de API (REST)

- **`ether_ocr.api.server`**: factory `create_app()` que construye la app
  FastAPI con CORS, routers y documentacion OpenAPI automatica.
- **`ether_ocr.api.routes.health`**: `GET /api/v1/health` — health check
  publico sin autenticacion.
- **`ether_ocr.api.routes.ocr`**: `POST /api/v1/ocr` — OCR/extraccion de
  un archivo. `POST /api/v1/ocr/batch` — procesamiento por lotes.
  Textos >100KB se devuelven como `tar.gz` via StreamingResponse.
- **`ether_ocr.api.routes.prepare`**: `POST /api/v1/prepare` y
  `POST /api/v1/validate` — preparacion y validacion de texto.
- **`ether_ocr.api.auth`**: modulo de autenticacion con soporte dual:
  API key (`X-API-Key`) y JWT (`Authorization: Bearer`). Desactivable
  con `AUTH_ENABLED=0` para desarrollo.
- **`ether_ocr.api.schemas`**: modelos Pydantic v2 para request/response
  de todos los endpoints.

## Endpoints

| Metodo | Ruta | Auth | Descripcion |
|--------|------|------|-------------|
| `GET` | `/api/v1/health` | No | Health check del servicio |
| `POST` | `/api/v1/ocr` | Si | OCR/extraccion de un archivo |
| `POST` | `/api/v1/ocr/batch` | Si | OCR batch (multiple archivos) |
| `POST` | `/api/v1/prepare` | Si | Preparar documento como texto limpio |
| `POST` | `/api/v1/validate` | Si | Validar compatibilidad RAG |
| `GET` | `/docs` | No | Swagger UI (OpenAPI) |
| `GET` | `/redoc` | No | ReDoc (OpenAPI) |
| `GET` | `/openapi.json` | No | Esquema OpenAPI |

## Flujo principal (API)

1. Cliente envia `POST /api/v1/ocr` con archivo (multipart/form-data).
2. Middleware de auth verifica `X-API-Key` o JWT (si `AUTH_ENABLED=1`).
3. El endpoint valida tipo MIME y extension.
4. `pipeline.ocr_document()` decide automaticamente:
   - PDF con capa de texto → Poppler (`pdftotext`)
   - PDF escaneado → `pdf2image` + Tesseract OCR
   - Imagen → Tesseract OCR directo
   - Texto plano → passthrough con limpieza
5. Si `validate=true`, se ejecuta `validator.validate_plain_text()`.
6. Respuesta JSON con `{status, text, metadata}` o tar.gz si >100KB.

## Orquestacion

- **Makefile** (build): construccion, tests, lint, Docker, API.
- **Justfile** (tasks): OCR, Docker, API, utilidades.

## Contenedores

- `containers/Dockerfile`: multi-stage (`python:3.11-slim`), Poppler,
  Tesseract (spa+eng), FastAPI + uvicorn. HEALTHCHECK cada 30s.
- `containers/docker-compose.yml`: servicio API en puerto 8000, variables
  de entorno para auth, healthcheck integrado.
- `.env.example`: configuracion de auth, server y OCR.

## Dependencias entre capas

```
api/routes/ → api/schemas/ → (ninguna dependencia externa)
api/routes/ → pipeline, preparer, validator (capa de dominio)
api/auth.py → (solo FastAPI + stdlib)
pipeline → extractor, ocr, cleaner, validator
```

## Restricciones

- La capa `api/` depende de la capa de dominio, nunca al reves.
- Los PDFs escaneados requieren Tesseract instalado en el sistema.
- No acoplar esta herramienta al API de ingestion del RAG.
- Textos >100KB se devuelven comprimidos — no saturar respuestas HTTP.
