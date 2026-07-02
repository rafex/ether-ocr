# ether-cli-ocr

Interfaz de linea de comandos para OCR.

## Instalacion

```bash
pip install -e python/ether-core-ocr/ -e python/ether-cli-ocr/
```

## Uso

```bash
# OCR de PDF o imagen
ether-ocr ocr entrada.pdf salida.txt

# Preparar documento
ether-ocr prepare entrada.pdf salida.txt

# Validar texto para RAG
ether-ocr validate texto.txt
```
