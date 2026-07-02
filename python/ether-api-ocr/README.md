# ether-api-ocr

API REST con FastAPI para extraccion de texto y OCR.

## Endpoints

| Metodo | Ruta | Auth | Descripcion |
|--------|------|------|-------------|
| `GET` | `/api/v1/health` | No | Health check |
| `POST` | `/api/v1/ocr` | Si | OCR/extraccion de un archivo |
| `POST` | `/api/v1/ocr/batch` | Si | OCR batch (multiple archivos) |
| `POST` | `/api/v1/prepare` | Si | Preparar documento como texto limpio |
| `POST` | `/api/v1/validate` | Si | Validar compatibilidad RAG |

## Instalacion

```bash
pip install -e python/ether-core-ocr/ -e python/ether-api-ocr/
```

## Uso

```bash
ether-ocr-api
# o
python3 -m ether_ocr_api.server
```

## Configuracion

Ver `.env.example` en la raiz del repositorio.
