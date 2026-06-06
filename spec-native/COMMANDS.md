# COMMANDS.md

Lista de comandos operativos del proyecto.

## Setup

```bash
# Instalar dependencias del sistema (macOS/Debian/Fedora/Alpine)
bash scripts/shellscript/setup.sh

# Python + deps OCR y API
python3 -m pip install -e 'python[ocr,api]'

# Solo deps de API
python3 -m pip install -e 'python[api]'
```

## Desarrollo

```bash
# Ayuda de Make
make help

# Ayuda de Just
just --list
```

## API REST

```bash
# Iniciar servidor en local (http://localhost:8000)
make api
# o
just api
# o
python3 -m ether_ocr.api.server

# Health check
curl http://localhost:8000/api/v1/health

# OpenAPI docs
open http://localhost:8000/docs

# OCR via API (con autenticacion)
curl -X POST http://localhost:8000/api/v1/ocr \
  -H "X-API-Key: dev-key-ether-ocr" \
  -F "file=@documento.pdf" \
  -F "lang=spa+eng"

# OCR batch
curl -X POST http://localhost:8000/api/v1/ocr/batch \
  -H "X-API-Key: dev-key-ether-ocr" \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.pdf"
```

## OCR CLI

```bash
# OCR directo (sin API)
just ocr documento.pdf salida.txt
make ocr INPUT=documento.pdf OUTPUT=salida.txt
```

## Tests

```bash
# Todos los tests
make test
# o
PYTHONPATH=python/src python3 -m unittest discover -s python/tests
```

## Lint y formato

```bash
make lint
just lint
```

## Docker

```bash
# Build de la imagen
make docker-build
just docker-build

# Iniciar API en Docker (puerto 8000)
make docker-up
just docker-api

# Detener servicios
make docker-down
just docker-down

# Logs del contenedor
just docker-logs

# Shell interactivo en contenedor
make docker-shell
just docker-shell

# OCR dentro del contenedor
just docker-ocr entrada.pdf salida.txt
```

## Utilidad

```bash
# Preparar documento
PYTHONPATH=python/src python3 -m ether_ocr prepare entrada.pdf salida.txt

# Validar texto
PYTHONPATH=python/src python3 -m ether_ocr validate texto.txt

# Limpiar build artifacts
make clean
just clean
```
