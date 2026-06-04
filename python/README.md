# ether-ocr Python

Herramienta para preparar documentos PDF o texto crudo como texto plano
UTF-8 compatible con el RAG de `faiss-poc`.

## Requisitos

- Python 3.11+
- Poppler para procesar PDFs:
  - macOS: `brew install poppler`
  - Debian/Ubuntu: `sudo apt install poppler-utils`

## Uso sin instalar

```bash
PYTHONPATH=python/src python3 -m ether_ocr prepare entrada.pdf salida.txt
PYTHONPATH=python/src python3 -m ether_ocr clean reglamento_raw.txt reglamento_limpio.txt
PYTHONPATH=python/src python3 -m ether_ocr validate reglamento_limpio.txt
```

## Uso instalado

```bash
python3 -m pip install -e python
ether-ocr prepare entrada.pdf salida.txt
```

## Tests

```bash
PYTHONPATH=python/src python3 -m unittest discover -s python/tests
```
