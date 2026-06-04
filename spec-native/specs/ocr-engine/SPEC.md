# SPEC.md

## Metadata

- ID: ocr-engine
- Estado: active
- Owner: rafex
- Fecha de creacion: 2026-06-03
- Ultima actualizacion: 2026-06-03

## Problema

Los PDFs escaneados o imagenes sin capa de texto no pueden procesarse con
`pdftotext` (Poppler). Se necesita un motor OCR que extraiga texto de
cualquier entrada visual (PDF escaneado, PNG, JPEG, TIFF) y entregue
texto plano UTF-8 compatible con el pipeline RAG existente.

## Objetivo

Crear un motor OCR en Python (POC) usando Tesseract, disenado para
ejecutarse en contenedores Docker, con orquestacion via Makefile
(build) y Justfile (tasks) que delegan exclusivamente a scripts
en `scripts/`. El diseno debe anticipar la migracion futura a Rust.

## Alcance

- OCR de imagenes (PNG, JPEG, TIFF) y PDFs escaneados via Tesseract.
- Conversion de PDF escaneado a imagenes con `pdf2image` + Poppler.
- Integracion con el pipeline existente (`extractor`, `cleaner`, `validator`).
- Nuevo comando CLI `ocr` en `python -m ether_ocr`.
- Scripts orquestables en `scripts/python/`, `scripts/shellscript/`,
  `scripts/mk/`, `scripts/just/`.
- Makefile que solo orquesta scripts de `scripts/mk/` y `scripts/shellscript/`.
- Justfile que solo orquesta scripts de `scripts/just/` y `scripts/python/`.
- Contenedor Docker con Tesseract + Poppler + Python 3.11.
- `docker-compose.yml` para desarrollo local.

## Fuera de alcance

- Migracion a Rust en esta iniciativa.
- OCR de video o streaming.
- Entrenamiento de modelos Tesseract personalizados.
- Subida automatica al RAG (sigue siendo iniciativa separada).
- Procesamiento distribuido o colas de trabajo.

## Criterios de aceptacion

- Dado un PDF escaneado (sin capa de texto), `just ocr entrada.pdf salida.txt`
  genera texto UTF-8.
- Dada una imagen PNG/JPEG, `make ocr-image entrada.png salida.txt` genera
  texto UTF-8.
- `make build` construye la imagen Docker sin errores.
- `make test` ejecuta los tests unitarios dentro del contenedor.
- `just lint` ejecuta linting sobre el codigo Python.
- Makefile y Justfile no contienen logica inline — solo llaman scripts.
- Los scripts en `scripts/` son auto-contenidos y ejecutables directamente.
- El codigo nuevo (`ocr.py`, `pipeline.py`) tiene tests unitarios.

## Validacion

```bash
# Tests unitarios (sin requerir Tesseract instalado en host)
make test

# Build de imagen Docker
make docker-build

# OCR dentro del contenedor
just docker-ocr muestra_escaneada.pdf salida.txt

# Lint
just lint
```

## Riesgos

- Calidad del OCR variable segun calidad de la imagen escaneada.
- Tesseract requiere datos de idioma (`spa.traineddata`, `eng.traineddata`).
- La conversion PDF→imagen puede ser lenta para documentos grandes.
- El pipeline Python → Rust debe mantener compatibilidad de interfaces CLI.
