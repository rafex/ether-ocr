# SPEC.md

## Metadata

- ID: rest-api
- Estado: done
- Owner: rafex
- Fecha de creacion: 2026-06-04
- Ultima actualizacion: 2026-06-06

## Problema

`ether-ocr` es actualmente una CLI — no puede ser consumido por agentes
de IA ni pipelines RAG como servicio HTTP. Se necesita una API REST que
exponga las capacidades de OCR, preparacion y validacion como endpoints
accesibles desde cualquier lenguaje o plataforma.

## Objetivo

Exponer `ether-ocr` como API REST con FastAPI, empaquetada en Docker,
que acepte PDFs, imagenes y texto plano, y devuelva texto UTF-8 limpio
con metadatos. La API debe ser autocontenida, autenticada y lista para
produccion.

## Alcance

### Endpoints

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| `POST` | `/api/v1/ocr` | Subir PDF/imagen, devuelve texto OCR + metadatos |
| `POST` | `/api/v1/prepare` | Subir PDF/texto, devuelve texto limpio validado |
| `POST` | `/api/v1/validate` | Validar si un texto es compatible con RAG |
| `GET` | `/api/v1/health` | Health check del servicio |

### Funcionalidades

- **Autenticacion**: API key via header `X-API-Key` o JWT `Authorization: Bearer`.
- **Batch**: aceptar multiples archivos en una sola peticion (`multipart/form-data`
  con campo `files` multiple).
- **Metadatos en respuesta**: paginas procesadas, confianza OCR promedio,
  idioma detectado, tamanio del texto resultante, metodo usado (poppler/ocr).
- **Textos largos**: si el texto extraido supera 100KB, devolver un archivo
  `.tar.gz` con el texto y metadatos en JSON, en lugar de texto inline.
- **Rate limiting**: limite de peticiones por API key.
- **Validacion de entrada**: tipo MIME, extension, tamanio maximo de archivo (50MB).

### Stack

- **Framework**: FastAPI + uvicorn
- **Validacion**: Pydantic v2
- **Auth**: python-jose (JWT) + API key middleware
- **Async**: endpoints async para no bloquear el event loop durante OCR
- **Contenedor**: mismo Dockerfile, stage adicional para API

## Fuera de alcance

- Insertar texto en `faiss-poc` u otro RAG (lo hace un agente externo).
- Interfaz grafica o frontend.
- Colas de trabajo (RabbitMQ, Redis) — para primera version.
- Rate limiting avanzado con Redis — usar limite en memoria para POC.
- Versionado de API mas alla de `/v1/`.

## Criterios de aceptacion

- `POST /api/v1/ocr` con un PDF escaneado devuelve 200 con texto UTF-8 y metadatos.
- `POST /api/v1/prepare` con un PDF con capa de texto devuelve 200 con texto limpio.
- `POST /api/v1/validate` con Markdown devuelve 422 con errores descriptivos.
- `GET /api/v1/health` devuelve 200 con `{"status": "ok"}`.
- Endpoints rechazan peticiones sin `X-API-Key` con 401.
- Batch de 5 archivos procesa todos y devuelve resultados individuales.
- Texto >100KB devuelve `application/gzip` con tar.gz.
- `make docker-build` construye la imagen con el servidor API incluido.
- Tests de integracion cubren todos los endpoints.

## Validacion

```bash
# Levantar servidor
make docker-build && just docker-up

# Health check
curl http://localhost:8000/api/v1/health

# OCR de un PDF
curl -X POST http://localhost:8000/api/v1/ocr \
  -H "X-API-Key: test-key" \
  -F "file=@escaneado.pdf"

# Tests de integracion
make test-api
```

## Riesgos

- OCR sincrono puede bloquear el event loop para PDFs muy grandes (>100 paginas).
  Mitigacion: usar `run_in_executor` para Tesseract, o background tasks.
- Tar.gz en memoria puede consumir mucha RAM para textos extremadamente largos.
  Mitigacion: escribir a disco temporal y hacer streaming.
- FastAPI + Tesseract en el mismo proceso puede tener memory leaks.
  Mitigacion: health check con restart automatico en docker-compose.
