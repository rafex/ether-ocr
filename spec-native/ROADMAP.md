# ROADMAP.md

Direccion del proyecto en el tiempo.

## Objetivo

Dar contexto de prioridad sin convertir esto en una lista de tickets.

## Cuando leer este archivo

Leer antes de crear una nueva spec para confirmar que la iniciativa
es coherente con la direccion actual del proyecto.

Si ROADMAP.md menciona una iniciativa pero no existe spec para ella,
el siguiente paso es crear esa spec antes de implementar.

## Roadmap actual

## Ahora

- **API REST**: exponer ether-ocr como servicio HTTP con FastAPI.
  Endpoints: OCR, preparacion, validacion. Autenticacion, batch,
  metadatos y respuestas comprimidas. Iniciativa activa: `rest-api`.
## Despues

- Evaluar comando de subida al API del RAG como iniciativa separada.
- Mejorar calidad OCR con preprocesamiento de imagen (thresholding,
  deskew, eliminacion de ruido).
### Mas adelante

- Version Rust bajo `rust/src` si se necesita mayor velocidad o binario
  autocontenido.

### No hacer por ahora

- No acoplar la herramienta al ciclo de vida interno de `faiss-poc`.
- No aceptar Markdown/HTML como salida final por defecto.
