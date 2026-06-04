# CONVENTIONS.md

Reglas operativas y de implementacion del proyecto.

## Codigo Python

- **Version minima**: Python 3.11+.
- **Naming**: snake_case para variables y funciones, PascalCase para clases.
- **Type hints**: obligatorios en todas las funciones publicas.
- **Docstrings**: toda funcion publica debe tener docstring con descripcion,
  `Args:`, `Returns:` y `Raises:`.
- **Imports**: orden stdlib → terceros → locales, separados por linea en blanco.
- **Formato**: ruff (linter + formatter), mypy para type checking.
- **Recursos**: usar `with` (context managers) para archivos, subprocess y
  directorios temporales. Nunca dejar file handles abiertos.
- **Errores**: usar excepciones propias (`OcrError`, `PdfExtractionError`,
  `ValidationError`), no `except Exception` generico.
- **Codigo fuente**: vive en `python/src/ether_ocr/`. Tests en `python/tests/`.

## API REST

- **Framework**: FastAPI (preferido) o Flask. Definir en la spec de la iniciativa.
- **Endpoints**: usar prefijo `/api/v1/` para versionado.
- **Autenticacion**: header `Authorization: Bearer <token>` o `X-API-Key`.
- **Respuestas**: JSON con schema consistente. Campos obligatorios: `status`,
  `data` o `error`.
- **Archivos grandes**: si el texto extraido supera 100KB, devolver una
  referencia a un archivo comprimido (tar.gz) o un JSON con URL de descarga.
- **Validacion**: usar Pydantic para schemas de request/response.
- **Errores HTTP**: 400 para validacion, 401 para auth, 413 para archivos
  demasiado grandes, 422 para formato no soportado, 500 para errores internos.

## Scripts

- Los scripts viven en `scripts/python/`, `scripts/shellscript/`,
  `scripts/mk/` y `scripts/just/`.
- Cada script es auto-contenido: se puede ejecutar directamente sin
  el wrapper Make/Just.
- **Shell scripts**: `#!/usr/bin/env bash`, `set -euo pipefail` obligatorio.
  Variables entre comillas (`"$var"`). No usar `ls` para parsear.
- **Python scripts**: shebang `#!/usr/bin/env python3`, ejecutables (`chmod +x`).
  Usan `argparse` para CLI. Devuelven exit code 0 en exito, 1 en error.
- **Make y Just**: solo orquestan scripts. **Nunca** contienen logica inline
  (no bucles, no condicionales complejos, no comandos directos salvo `echo`
  informativos). Si se necesita logica, va en un script.

## Commits

- **Formato**: Conventional Commits con emojis.
  ```
  ✨ feat(scope): descripcion en espanol
  ```
- **Tipos**: feat, fix, docs, style, refactor, perf, test, build, ci, chore.
- **Scopes**: modulo afectado (ocr, api, pipeline, cli, docker, docs).
- **Atomicos**: un solo proposito por commit. Si el diff tiene cambios no
  relacionados, dividir en multiples commits.
- **Idioma**: espanol para la descripcion.

## Testing

- **Framework**: `unittest` (stdlib). No introducir pytest sin decision explicita.
- **Unitarios**: no requieren dependencias externas (Tesseract, Poppler).
  Usar `unittest.mock` para aislar.
- **Cobertura**: toda funcion publica nueva debe tener al menos un test.
- **Ubicacion**: `python/tests/test_<modulo>.py`.

## Seguridad

- **Secretos**: nunca hardcodear API keys, tokens ni passwords. Usar variables
  de entorno (`os.environ`).
- **Subprocess**: siempre usar listas (no `shell=True`) para prevenir command
  injection. Validar inputs antes de pasarlos a comandos externos.
- **Archivos temporales**: usar `tempfile.TemporaryDirectory` con `with`.
- **Uploads**: validar tipo MIME y extension. Limitar tamanio maximo de archivo.
- **Rate limiting**: implementar en la API REST para evitar abuso.

## Documentacion

- Los `README.md` indexan y enrutan. No reemplazan el contexto fuente.
- Los archivos en MAYUSCULAS en `spec-native/` contienen la verdad del proyecto.
- No duplicar hechos entre documentos sin una razon fuerte.
- Actualizar el documento fuente cuando cambia una verdad compartida.
- Toda nueva iniciativa debe tener spec en `spec-native/specs/<iniciativa>/SPEC.md`
  y tareas en `spec-native/tasks/<iniciativa>/TASKS.md`.
