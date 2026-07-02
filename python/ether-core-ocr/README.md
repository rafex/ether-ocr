# ether-core-ocr

Motor OCR y dominio compartido de ether-ocr.

## Modulos

- `pipeline.py` — orquesta extraccion Poppler o OCR segun tipo de entrada
- `ocr.py` — motor OCR con Tesseract para PDFs escaneados e imagenes
- `extractor.py` — extrae texto de PDFs con capa de texto via Poppler
- `cleaner.py` — normaliza artefactos de layout PDF
- `validator.py` — valida compatibilidad RAG (UTF-8 plano, sin Markdown/HTML)
- `preparer.py` — pipeline de preparacion high-level

## Dependencias

- Python 3.11+
- Poppler (`pdftotext`) — requerido para extraccion de PDFs
- Tesseract OCR — requerido para OCR de escaneados/imagenes

## Instalacion

```bash
pip install -e python/ether-core-ocr/
```
