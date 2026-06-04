# TRACEABILITY.md

Mapa de relaciones entre specs, tareas, decisiones y validacion.

## Objetivo

Permitir que una persona o agente pueda reconstruir rapidamente:

- que spec origino un cambio
- que tareas ejecutaron esa spec
- que decisiones condicionaron el trabajo
- que evidencia valida el resultado

## Cuando actualizar este archivo

Actualizar al cerrar una iniciativa, no durante la ejecucion.
El momento correcto es cuando la spec pasa a estado `done` o `blocked`.

Si una decision cambia el alcance de una spec activa, registrar
la relacion antes de continuar.

## Formato sugerido

| Spec | Estado | Tareas | Decisiones | Archivos principales | Validacion | Observaciones |
| --- | --- | --- | --- | --- | --- | --- |
| pdf-to-rag-text | done | TASK-0001, TASK-0002, TASK-0003, TASK-0004 | DEC-0001 | `python/src/ether_ocr/*`, `python/tests/*` | `PYTHONPATH=python/src python3 -m unittest discover -s python/tests` | Genera texto plano UTF-8 para el RAG de `faiss-poc`. |
| ocr-engine | active | TASK-OCR-0001, TASK-OCR-0002, TASK-OCR-0003, TASK-OCR-0004, TASK-OCR-0005 | DEC-0002 | `python/src/ether_ocr/ocr.py`, `python/src/ether_ocr/pipeline.py`, `python/tests/test_ocr.py`, `python/tests/test_pipeline.py`, `scripts/`, `Makefile`, `Justfile`, `containers/` | `make test`, `make docker-build` | OCR con Tesseract para PDFs escaneados e imagenes. Orquestado via Make/Just, contenerizado con Docker. |
