# ARCHITECTURE.md

Describe la arquitectura actual del proyecto.

## Debe responder

- Cuales son los modulos o bounded contexts principales.
- Que responsabilidad tiene cada modulo.
- Donde estan los limites entre capas.
- Que dependencias estan permitidas o prohibidas.
- Cuales son los puntos de integracion externos.

## Arquitectura actual

### Vision general

`ether-ocr` prepara documentos para alimentar un RAG externo que solo
acepta texto plano UTF-8. La primera implementacion vive en Python bajo
`python/src` y separa la extraccion PDF, limpieza de texto, validacion
de formato plano y CLI.

El sistema no sube documentos al RAG. Su salida es un `.txt` limpio que
puede enviarse despues al backend de `/Users/rafex/repository/github/rafex/faiss-poc`.

## Modulos principales

- `ether_ocr.extractor`: invoca `pdftotext -layout` para convertir PDFs
  con capa de texto a texto crudo.
- `ether_ocr.ocr`: motor OCR con Tesseract para PDFs escaneados e imagenes.
  Soporta `ocr_image()` para imagenes y `ocr_pdf_scanned()` para PDFs via
  `pdf2image` + Poppler.
- `ether_ocr.pipeline`: orquesta extraccion Poppler o OCR segun el tipo
  de entrada. Decide automaticamente si el PDF tiene capa de texto o
  requiere OCR.
- `ether_ocr.cleaner`: normaliza artefactos de layout PDF, numeracion
  de pagina, espacios repetidos y separadores de articulos/secciones.
- `ether_ocr.validator`: rechaza Markdown, HTML y caracteres de control
  para alinear la salida con el validador del RAG.
- `ether_ocr.preparer`: orquesta entrada, limpieza, validacion y escritura
  del archivo final.
- `ether_ocr.cli`: expone comandos `prepare`, `clean`, `validate` y `ocr`.
## Flujo principal

1. Recibir ruta de entrada `.pdf`, imagen (`.png`, `.jpg`, `.tiff`) o texto UTF-8.
2. Si es imagen, ejecutar OCR directo con Tesseract.
3. Si es PDF:
   a. Intentar extraccion de texto con Poppler (`pdftotext -layout`).
   b. Si el texto extraido es insuficiente (<10 chars), verificar capa de texto.
   c. Si no tiene capa de texto, convertir paginas a imagenes y ejecutar OCR.
4. Limpiar artefactos de layout.
5. Validar texto plano compatible con RAG.
6. Escribir archivo `.txt` UTF-8.
### Restricciones

- Los PDFs escaneados sin capa de texto estan fuera de alcance por ahora.
- No acoplar esta herramienta al API de subida del RAG.
- Mantener codigo Python en `python/src`; si aparece Rust, usar
  `rust/src`.

### Riesgos

- PDF sin capa de texto: la salida puede estar vacia. Mitigacion futura:
  incorporar OCR explicitamente como nueva iniciativa.
- Falsos positivos del validador: Markdown tecnico legitimo puede ser
  rechazado. Mitigacion: permitir `--skip-validation` solo para casos
  revisados manualmente.

## Orquestacion

El proyecto usa un sistema de orquestacion en dos capas:

- **Makefile** (build): orquesta construccion, tests, lint y operaciones
  Docker. Delega a scripts en `scripts/python/`, `scripts/shellscript/` y
  `scripts/mk/`. No contiene logica inline.
- **Justfile** (tasks): task runner para desarrollo diario. Orquesta OCR,
  Docker y utilidades. Importa modulos de `scripts/just/` y delega a
  `scripts/python/`.

### Estructura de scripts

```
scripts/
├── python/          ← Scripts Python (build, test, ocr, lint)
├── shellscript/     ← Shell scripts (docker-build, docker-run, setup)
├── mk/              ← Includes reusables de Make (docker.mk)
└── just/            ← Includes reusables de Just (dev.just, docker.just)
```

## Contenedores

El sistema esta disenado para ejecutarse en contenedores Docker:

- `containers/Dockerfile`: multi-stage con `python:3.11-slim`, Poppler y
  Tesseract OCR (espanol + ingles).
- `containers/docker-compose.yml`: entorno de desarrollo con volumenes
  para codigo fuente y datos.
- Todas las dependencias de sistema (Poppler, Tesseract) se instalan en
  la imagen — no se requieren en el host.
