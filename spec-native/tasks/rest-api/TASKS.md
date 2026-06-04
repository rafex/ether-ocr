# TASKS.md

## Metadata

- Iniciativa: rest-api
- Spec relacionada: `spec-native/specs/rest-api/SPEC.md`
- Owner: rafex
- Estado general: todo

## Tareas

### TASK-API-0001 — Servidor FastAPI base + health endpoint

- ID: TASK-API-0001
- Title: Servidor FastAPI base + health endpoint
- State: done
- Owner: rafex
- Dependencies: none
- Expected files: `python/src/ether_ocr/api/__init__.py`, `python/src/ether_ocr/api/server.py`, `python/src/ether_ocr/api/routes/health.py`
- Close criteria: `GET /api/v1/health` responde 200 con `{"status": "ok"}`.
- Validation: `curl http://localhost:8000/api/v1/health` → `{"status":"ok","version":"0.2.0","service":"ether-ocr"}`

### TASK-API-0002 — Endpoint OCR (/api/v1/ocr)

- ID: TASK-API-0002
- Title: Endpoint OCR (/api/v1/ocr)
- State: todo
- Owner: rafex
- Dependencies: TASK-API-0001
- Expected files: `python/src/ether_ocr/api/routes/ocr.py`, `python/src/ether_ocr/api/schemas/ocr.py`
- Close criteria: `POST /api/v1/ocr` acepta PDF/imagen, devuelve texto + metadatos.
- Validation: Test con PDF escaneado real y mock.

### TASK-API-0003 — Endpoint Prepare y Validate

- ID: TASK-API-0003
- Title: Endpoint Prepare y Validate
- State: todo
- Owner: rafex
- Dependencies: TASK-API-0001
- Expected files: `python/src/ether_ocr/api/routes/prepare.py`, `python/src/ether_ocr/api/routes/validate.py`, `python/src/ether_ocr/api/schemas/prepare.py`
- Close criteria: `POST /api/v1/prepare` y `POST /api/v1/validate` funcionales.
- Validation: Tests de integracion.

### TASK-API-0004 — Autenticacion (API key + JWT)

- ID: TASK-API-0004
- Title: Autenticacion (API key + JWT)
- State: todo
- Owner: rafex
- Dependencies: TASK-API-0001
- Expected files: `python/src/ether_ocr/api/auth.py`, `python/src/ether_ocr/api/middleware.py`
- Close criteria: Endpoints rechazan 401 sin credenciales. API key y JWT funcionales.
- Validation: `curl` sin header → 401, con header → 200.

### TASK-API-0005 — Soporte batch y textos largos

- ID: TASK-API-0005
- Title: Soporte batch y textos largos
- State: todo
- Owner: rafex
- Dependencies: TASK-API-0002, TASK-API-0003
- Expected files: `python/src/ether_ocr/api/batch.py`, `python/src/ether_ocr/api/compression.py`
- Close criteria: Batch procesa N archivos. Texto >100KB devuelve tar.gz.
- Validation: Test con 5 archivos batch. Test con texto sintetico >100KB.

### TASK-API-0006 — Dockerizacion del servidor API

- ID: TASK-API-0006
- Title: Dockerizacion del servidor API
- State: todo
- Owner: rafex
- Dependencies: TASK-API-0001, TASK-API-0002, TASK-API-0003, TASK-API-0004, TASK-API-0005
- Expected files: `containers/Dockerfile` (actualizado), `containers/docker-compose.yml` (actualizado)
- Close criteria: `make docker-build` construye imagen con API. `just docker-up` levanta servidor.
- Validation: `curl http://localhost:8000/api/v1/health` dentro del contenedor.

### TASK-API-0007 — Tests de integracion y documentacion

- ID: TASK-API-0007
- Title: Tests de integracion y documentacion
- State: todo
- Owner: rafex
- Dependencies: TASK-API-0006
- Expected files: `python/tests/test_api.py`, `spec-native/ARCHITECTURE.md`, `spec-native/COMMANDS.md`, `README.md`
- Close criteria: Tests de integracion cubren todos los endpoints. Documentacion actualizada.
- Validation: `make test-api`, revision documental.
