# ether-ocr

Motor OCR y preparador de documentos para convertir PDFs (con o sin capa
de texto) e imágenes a texto plano UTF-8 listo para RAG.

## Inicio rápido

```bash
# Instalar dependencias del sistema
bash scripts/shellscript/setup.sh

# O usar Docker (no requiere instalar nada en el host)
make docker-build
just docker-ocr documento.pdf salida.txt
```

## Orquestación

El proyecto usa dos orquestadores que delegan a scripts — **sin lógica inline**:

| Herramienta | Propósito | Scripts |
|---|---|---|
| `make` | Build, test, lint, Docker | `scripts/mk/`, `scripts/shellscript/` |
| `just` | Tasks diarias (OCR, dev, Docker) | `scripts/just/`, `scripts/python/` |

```bash
make help      # Ver targets disponibles
just --list    # Ver recipes disponibles
```

## Python

```bash
# OCR de imagen o PDF escaneado
PYTHONPATH=python/src python3 -m ether_ocr ocr escaneado.pdf salida.txt

# Preparar PDF con capa de texto (Poppler)
PYTHONPATH=python/src python3 -m ether_ocr prepare entrada.pdf salida.txt

# Validar texto para RAG
PYTHONPATH=python/src python3 -m ether_ocr validate salida.txt

# Tests
make test
```

## Docker

```bash
# Build de la imagen (Python 3.11 + Poppler + Tesseract spa/eng)
make docker-build

# OCR dentro del contenedor
just docker-ocr escaneado.pdf salida.txt

# Shell interactivo
make docker-shell

# Entorno de desarrollo con docker-compose
just docker-up
```

## Dependencias del sistema

| Herramienta | Para |
|---|---|
| Poppler (`pdftotext`) | Extraer texto de PDFs con capa de texto |
| Tesseract OCR | OCR de PDFs escaneados e imágenes |

Ambas se instalan automáticamente con `scripts/shellscript/setup.sh` o
vienen incluidas en la imagen Docker.

## Estructura

```
├── python/src/ether_ocr/   ← Paquete Python (extractor, ocr, cleaner, validator, pipeline, cli)
├── python/tests/            ← Tests unitarios
├── scripts/                 ← Scripts orquestables
│   ├── python/              ← Scripts Python (build, test, ocr, lint)
│   ├── shellscript/         ← Shell scripts (docker, setup)
│   ├── mk/                  ← Includes de Makefile
│   └── just/                ← Includes de Justfile
├── containers/              ← Dockerfile + docker-compose
├── Makefile                 ← Build orchestrator
├── Justfile                 ← Task runner
└── spec-native/             ← Contexto SpecNative del proyecto
```

## Roadmap

- ✅ Preparador PDF→texto con Poppler
- 🔄 Motor OCR con Tesseract (POC Python)
- ⏳ Preprocesamiento de imagen (deskew, thresholding)
- ⏳ Migración a Rust
