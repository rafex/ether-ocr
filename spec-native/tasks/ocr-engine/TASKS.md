# TASKS.md

## Metadata

- Iniciativa: ocr-engine
- Spec relacionada: `spec-native/specs/ocr-engine/SPEC.md`
- Owner: rafex
- Estado general: done

## Tareas

### TASK-OCR-0001 — Estructura de scripts/ y orquestadores

- ID: TASK-OCR-0001
- Title: Estructura de scripts/ y orquestadores
- State: done
- Owner: rafex
- Dependencies: none
- Expected files: `Makefile`, `Justfile`, `scripts/mk/docker.mk`, `scripts/just/dev.just`, `scripts/just/docker.just`
- Close criteria: Makefile y Justfile existen, delegan a scripts, no contienen logica inline.
- Validation: `make help` y `just --list` muestran los targets disponibles.

### TASK-OCR-0002 — Scripts Python del pipeline

- ID: TASK-OCR-0002
- Title: Scripts Python del pipeline
- State: done
- Owner: rafex
- Dependencies: TASK-OCR-0001
- Expected files: `scripts/python/build.py`, `scripts/python/test.py`, `scripts/python/ocr.py`, `scripts/python/lint.py`
- Close criteria: Cada script es auto-contenido y ejecutable con `python3 scripts/python/<script>.py`.
- Validation: Ejecucion manual de cada script.

### TASK-OCR-0003 — Motor OCR en Python

- ID: TASK-OCR-0003
- Title: Motor OCR en Python
- State: done
- Owner: rafex
- Dependencies: TASK-OCR-0002
- Expected files: `python/src/ether_ocr/ocr.py`, `python/src/ether_ocr/pipeline.py`, `python/tests/test_ocr.py`, `python/tests/test_pipeline.py`
- Close criteria: OCR funcional con Tesseract, integrado al pipeline existente, con tests unitarios.
- Validation: `make test`

### TASK-OCR-0004 — Scripts shell y configuracion Docker

- ID: TASK-OCR-0004
- Title: Scripts shell y configuracion Docker
- State: done
- Owner: rafex
- Dependencies: TASK-OCR-0003
- Expected files: `scripts/shellscript/docker-build.sh`, `scripts/shellscript/docker-run.sh`, `scripts/shellscript/setup.sh`, `containers/Dockerfile`, `containers/docker-compose.yml`
- Close criteria: `make docker-build` construye la imagen, `just docker-run` ejecuta el OCR en contenedor.
- Validation: Build exitoso de la imagen Docker, OCR funcional dentro del contenedor.

### TASK-OCR-0005 — Documentacion y cierre

- ID: TASK-OCR-0005
- Title: Documentacion y cierre
- State: done
- Owner: rafex
- Dependencies: TASK-OCR-0001, TASK-OCR-0002, TASK-OCR-0003, TASK-OCR-0004
- Expected files: `spec-native/ARCHITECTURE.md`, `spec-native/STACK.md`, `spec-native/COMMANDS.md`, `spec-native/ROADMAP.md`, `spec-native/DECISIONS.md`, `spec-native/TRACEABILITY.md`, `README.md`
- Close criteria: Documentos fuente de verdad actualizados, trazabilidad registrada.
- Validation: Revision documental completa.
