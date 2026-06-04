# TASKS.md

## Metadata

- Iniciativa: pdf-to-rag-text
- Spec relacionada: `spec-native/specs/pdf-to-rag-text/SPEC.md`
- Owner: rafex
- Estado general: done

## Tareas

### TASK-0001 - Definir iniciativa SpecNative

- ID: TASK-0001
- Title: Definir iniciativa SpecNative
- State: done
- Owner: Codex
- Dependencies:
- Expected files: `spec-native/specs/pdf-to-rag-text/SPEC.md`, `spec-native/tasks/pdf-to-rag-text/TASKS.md`
- Close criteria: La iniciativa tiene spec activa, alcance y criterios de aceptacion.
- Validation: Revision documental.

### TASK-0002 - Implementar preparador Python

- ID: TASK-0002
- Title: Implementar preparador Python
- State: done
- Owner: Codex
- Dependencies: TASK-0001
- Expected files: `python/src/ether_ocr/**`
- Close criteria: Existe CLI Python para preparar PDFs o texto crudo hacia texto plano UTF-8 compatible con el RAG.
- Validation: `python3 -m unittest discover -s python/tests`

### TASK-0003 - Documentar comandos y arquitectura

- ID: TASK-0003
- Title: Documentar comandos y arquitectura
- State: done
- Owner: Codex
- Dependencies: TASK-0002
- Expected files: `spec-native/ARCHITECTURE.md`, `spec-native/STACK.md`, `spec-native/COMMANDS.md`, `README.md`
- Close criteria: Los documentos fuente de verdad explican estructura, runtime y comandos de validacion.
- Validation: Revision documental.

### TASK-0004 - Validar cierre

- ID: TASK-0004
- Title: Validar cierre
- State: done
- Owner: Codex
- Dependencies: TASK-0002, TASK-0003
- Expected files: `python/tests/**`, `spec-native/TRACEABILITY.md`, `spec-native/SESSION.md`
- Close criteria: Tests ejecutados, tareas cerradas y trazabilidad registrada.
- Validation: `python3 -m unittest discover -s python/tests`
