# STACK.md

Fuente de verdad de la base tecnologica del proyecto.

## Debe responder

- Que tecnologias usa el proyecto.
- Que versiones o rangos son obligatorios.
- Que servicios externos participan.
- Que restricciones de plataforma existen.

## Stack actual

### Runtime

- Lenguaje: Python
- Version: Python 3.11+

### Frameworks

- Sin framework obligatorio. La implementacion usa libreria estandar.

### Infraestructura

- Base de datos: no aplica.
- Hosting: no aplica.
- CI/CD: no configurado todavia.
- Observabilidad: salida CLI por stdout/stderr.

## Integraciones

- Poppler `pdftotext`: extrae texto de PDFs con capa de texto. Es una
  dependencia externa de sistema, requerida solo para entradas `.pdf`.
- Tesseract OCR: motor de reconocimiento optico de caracteres para PDFs
  escaneados e imagenes. Dependencia externa de sistema con datos de
  idioma (`spa`, `eng`).
- `pdf2image` (Python): convierte paginas de PDF a imagenes PNG para
  alimentar Tesseract. Requiere Poppler.
- `pytesseract` (Python): wrapper Python para Tesseract OCR.
- `faiss-poc`: consumidor esperado de los `.txt` generados; no hay
  integracion directa desde este repositorio.
- Docker: contenerizacion para desarrollo y despliegue.
### Restricciones

- El texto final debe ser UTF-8.
- El texto final debe evitar Markdown, HTML y caracteres de control.
- El codigo Python vive en `python/src`.
- Si se agrega Rust, el codigo fuente debe vivir en `rust/src`.

## Herramientas de desarrollo

- **Make**: build orchestrator. Solo orquesta scripts, sin logica inline.
- **Just**: task runner. Solo orquesta scripts, sin logica inline.
- **ruff**: linter y formateador Python.
- **mypy**: type checker estatico.
- **Docker**: contenerizacion.
- **unittest**: framework de testing (stdlib).

## Dependencias opcionales

Instalables con `pip install -e 'python[ocr]'`:
- `pytesseract>=0.3`
- `pdf2image>=1.17`
- `pillow>=10`

Instalables con `pip install -e 'python[dev]'`:
- `ruff>=0.6`
- `mypy>=1.11`
- `black>=24`
- `isort>=5`
