# COMMANDS.md

Lista de comandos operativos del proyecto.

## Objetivo

Reducir la ambiguedad de ejecucion para agentes y humanos.

## Comandos actuales

### Setup

```bash
# Instalar dependencias del sistema (macOS/Debian/Fedora/Alpine)
bash scripts/shellscript/setup.sh

# O solo Python + deps opcionales
python3 -m pip install -e 'python[ocr]'
```

### Desarrollo

```bash
# Ayuda de Make (build orchestrator)
make help

# Ayuda de Just (task runner)
just --list

# CLI Python
PYTHONPATH=python/src python3 -m ether_ocr --help
```

### OCR

```bash
# OCR de imagen
make ocr-image INPUT=escaneo.png OUTPUT=salida.txt

# OCR con Just
just ocr documento.pdf salida.txt

# OCR dentro del contenedor Docker
just docker-ocr escaneo.pdf salida.txt
```

### Tests

```bash
# Todos los tests
make test

# Solo tests unitarios
PYTHONPATH=python/src python3 -m unittest discover -s python/tests
```

### Lint y formato

```bash
make lint

# Solo formateo
just format
```

### Build y Docker

```bash
# Build de la imagen Docker
make docker-build

# Ejecutar OCR en contenedor
just docker-run entrada.pdf salida.txt

# Shell interactivo en contenedor
make docker-shell
```

### Utilidad

```bash
PYTHONPATH=python/src python3 -m ether_ocr prepare entrada.pdf salida.txt
PYTHONPATH=python/src python3 -m ether_ocr ocr escaneado.pdf salida.txt
PYTHONPATH=python/src python3 -m ether_ocr validate salida.txt
make clean
just clean
```
### Setup

```bash
# PDFs en macOS
brew install poppler

# PDFs en Debian/Ubuntu
sudo apt install poppler-utils

# instalacion editable opcional
python3 -m pip install -e python
```

### Desarrollo

```bash
PYTHONPATH=python/src python3 -m ether_ocr --help
```

### Tests

```bash
PYTHONPATH=python/src python3 -m unittest discover -s python/tests
```

### Lint y formato

```bash
# no configurado todavia
```

### Build

```bash
# no configurado todavia
```

### Utilidad

```bash
PYTHONPATH=python/src python3 -m ether_ocr prepare entrada.pdf salida.txt
PYTHONPATH=python/src python3 -m ether_ocr clean reglamento_raw.txt reglamento_limpio.txt
PYTHONPATH=python/src python3 -m ether_ocr validate reglamento_limpio.txt
```
