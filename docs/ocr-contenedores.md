# OCR por Contenedores

`ether-ocr` se distribuye como imagen Docker autocontenida que incluye
Poppler (`pdftotext`), Tesseract OCR (español + inglés) y la API REST
con FastAPI. No requiere instalar dependencias en el host.

## Modos de uso

| Modo | Comando | Descripción |
|---|---|---|
| CLI OCR | `docker run ether-ocr ocr entrada.pdf salida.txt` | Ejecución puntual de OCR sobre un archivo |
| API REST | `docker compose up -d` | Servicio persistente con endpoints HTTP |

## Prerrequisitos

- Docker 24+
- Docker Compose v2+

## Construir la imagen

```bash
# Desde la raíz del proyecto
make docker-build

# O manualmente
docker build -t ether-ocr:latest -f containers/Dockerfile .
```

La imagen se basa en `python:3.11-slim` y pesa ~400 MB.

## Modo 1 — CLI OCR (ejecución puntual)

Procesa un PDF o imagen y escribe el texto extraído a un archivo local.
La transferencia de archivos se hace por stdin/stdout, por lo que funciona
tanto con Docker/Podman local como remoto (no requiere volúmenes ni `docker cp`).

```bash
# Con Just (recomendado)
just docker-ocr entrada.pdf salida.txt

# O manualmente con pipe stdin/stdout
cat entrada.pdf | docker run --rm -i ether-ocr:latest \
  python3 -c "
import sys, tempfile
from pathlib import Path
from ether_ocr.pipeline import ocr_document

data = sys.stdin.buffer.read()

with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
    tmp.write(data)
    tmp_path = tmp.name

out_path = Path('/tmp/ocr_output.txt')

try:
    result = ocr_document(Path(tmp_path), out_path)
    print(f'Pages: {result.pages}', file=sys.stderr)
    print(f'Paragraphs: {result.paragraphs}', file=sys.stderr)
    print(f'Size: {result.size_bytes / 1024:.1f} KB', file=sys.stderr)
    print(f'OCR used: {\"yes\" if result.used_ocr else \"no\"}', file=sys.stderr)
    sys.stdout.write(out_path.read_text(encoding='utf-8'))
finally:
    Path(tmp_path).unlink(missing_ok=True)
    out_path.unlink(missing_ok=True)
" > salida.txt
```

### Parámetros del CLI OCR

| Argumento | Descripción |
|---|---|
| `input` | Ruta al PDF o imagen dentro del contenedor |
| `output` | Ruta de salida para el texto extraído |
| `--lang` | Idiomas OCR (default: `spa+eng`) |
| `--dpi` | DPI para conversión PDF→imagen (default: 300) |
| `--force-image` | Forzar OCR incluso si el PDF tiene capa de texto |
| `--no-validate` | Omitir validación RAG del texto extraído |

### Otros comandos CLI disponibles

```bash
# Preparar documento (solo PDF con capa de texto)
docker run --rm ether-ocr:latest \
  python3 -m ether_ocr prepare entrada.pdf salida.txt

# Validar texto para RAG
docker run --rm ether-ocr:latest \
  python3 -m ether_ocr validate texto.txt
```

## Modo 2 — API REST (servicio persistente)

Levanta un servidor HTTP en `http://localhost:8000` con endpoints de OCR,
preparación y validación.

### Iniciar el servicio

```bash
# Con docker compose (recomendado)
cp .env.example .env
make docker-up

# O manualmente
docker compose -f containers/docker-compose.yml up -d
```

### Detener el servicio

```bash
make docker-down
# o
docker compose -f containers/docker-compose.yml down
```

### Ver logs

```bash
just docker-logs
# o
docker compose -f containers/docker-compose.yml logs -f
```

## Configuración (variables de entorno)

Copiar `.env.example` a `.env` y ajustar valores:

### Autenticación

| Variable | Default | Descripción |
|---|---|---|
| `AUTH_ENABLED` | `1` | `0` para desactivar auth (solo desarrollo) |
| `API_KEYS` | `dev-key-ether-ocr` | API keys separadas por coma (hash SHA-256 en memoria) |
| `JWT_SECRET` | *(vacío)* | Secreto para verificar JWT. Vacío = JWT desactivado |

### Servidor

| Variable | Default | Descripción |
|---|---|---|
| `PORT` | `8000` | Puerto del servidor |
| `HOST` | `0.0.0.0` | Dirección de escucha |
| `CORS_ORIGINS` | `http://localhost:8000` | Orígenes CORS permitidos (separados por coma, `*` para todos) |
| `MAX_UPLOAD_BYTES` | `52428800` | Tamaño máximo de subida (50 MB) |

### Rate Limiting

| Variable | Default | Descripción |
|---|---|---|
| `RATE_LIMIT_ENABLED` | `1` | `0` para desactivar |
| `RATE_LIMIT_REQUESTS` | `30` | Máximo de peticiones por IP en la ventana |
| `RATE_LIMIT_WINDOW_SECONDS` | `60` | Ventana de rate limiting en segundos |

### OCR

| Variable | Default | Descripción |
|---|---|---|
| `OCR_DEFAULT_LANG` | `spa+eng` | Idiomas Tesseract por defecto |
| `OCR_DEFAULT_DPI` | `300` | DPI para conversión PDF→imagen |
| `OCR_MAX_INLINE_BYTES` | `102400` | Textos mayores se devuelven como `tar.gz` (100 KB) |

## Endpoints de la API

### `GET /api/v1/health` — Health check

Sin autenticación.

```bash
curl http://localhost:8000/api/v1/health
```

Respuesta:
```json
{"status": "ok", "version": "0.2.0"}
```

### `POST /api/v1/ocr` — Extraer texto de un documento

Requiere autenticación (`X-API-Key` o `Authorization: Bearer`).

```bash
curl -X POST http://localhost:8000/api/v1/ocr \
  -H "X-API-Key: dev-key-ether-ocr" \
  -F "file=@documento.pdf" \
  -F "lang=spa+eng" \
  -F "dpi=300" \
  -F "validate=true" \
  -F "force_image=false"
```

| Campo | Tipo | Default | Descripción |
|---|---|---|---|
| `file` | file | *(requerido)* | PDF, imagen o `.txt` |
| `lang` | string | `spa+eng` | Idiomas OCR (formato Tesseract) |
| `dpi` | int | `300` | DPI para rasterizado (72–600) |
| `validate` | bool | `true` | Validar compatibilidad RAG |
| `force_image` | bool | `false` | Forzar OCR ignorando capa de texto |

Respuesta (texto ≤100 KB):
```json
{
  "status": "ok",
  "text": "Artículo 1. Todo individuo tiene derecho...",
  "metadata": {
    "pages": 3,
    "paragraphs": 42,
    "size_bytes": 12345,
    "ocr_used": true,
    "method": "tesseract",
    "language": "spa+eng",
    "dpi": 300
  }
}
```

Para textos >100 KB la respuesta es un archivo `application/gzip` con un
`tar.gz` que contiene `<nombre>.txt` y `<nombre>.metadata.json`.

### `POST /api/v1/ocr/batch` — Procesar múltiples archivos

```bash
curl -X POST http://localhost:8000/api/v1/ocr/batch \
  -H "X-API-Key: dev-key-ether-ocr" \
  -F "files=@doc1.pdf" \
  -F "files=@doc2.pdf" \
  -F "lang=spa+eng"
```

Respuesta:
```json
{
  "status": "ok",
  "total_files": 2,
  "successful": 2,
  "failed": 0,
  "results": [
    {
      "filename": "doc1.pdf",
      "status": "ok",
      "text": "...",
      "metadata": { ... }
    }
  ]
}
```

### `POST /api/v1/prepare` — Preparar documento como texto limpio

Solo PDF con capa de texto o `.txt`. Usa Poppler para extracción directa.

```bash
curl -X POST http://localhost:8000/api/v1/prepare \
  -H "X-API-Key: dev-key-ether-ocr" \
  -F "file=@documento.pdf"
```

### `POST /api/v1/validate` — Validar texto para RAG

```bash
curl -X POST http://localhost:8000/api/v1/validate \
  -H "X-API-Key: dev-key-ether-ocr" \
  -F "file=@texto.txt"
```

Respuesta:
```json
{
  "status": "ok",
  "valid": true,
  "issues": []
}
```

### Documentación interactiva

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Autenticación

La API soporta dos métodos mutuamente excluyentes:

**API Key** — recomendado para agentes y pipelines:
```bash
curl -H "X-API-Key: dev-key-ether-ocr" http://localhost:8000/api/v1/ocr ...
```

**JWT** — para integración con sistemas de identidad:
```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/ocr ...
```

Para desarrollo local se puede desactivar con `AUTH_ENABLED=0` en `.env`.

## Formatos soportados

| Extensión | MIME type | Método |
|---|---|---|
| `.pdf` (con capa de texto) | `application/pdf` | Poppler (`pdftotext`) |
| `.pdf` (escaneado) | `application/pdf` | Poppler → imagen → Tesseract OCR |
| `.png`, `.jpg`, `.jpeg` | `image/png`, `image/jpeg` | Tesseract OCR directo |
| `.tiff`, `.tif` | `image/tiff` | Tesseract OCR directo |
| `.txt` | `text/plain` | Passthrough con limpieza |

## Pipeline inteligente

El sistema decide automáticamente el método de extracción:

1. Si `force_image=true` → fuerza OCR con Tesseract.
2. Si es `.txt` → limpia y valida, no aplica OCR.
3. Si es `.pdf` → intenta `pdftotext`. Si el resultado está vacío
   o tiene pocos caracteres, aplica OCR vía `pdf2image` + Tesseract.
4. Si es imagen → aplica Tesseract OCR directo.

## Respuesta para textos grandes

Cuando el texto extraído supera `OCR_MAX_INLINE_BYTES` (100 KB por defecto),
la API devuelve `Content-Type: application/gzip` con un archivo `tar.gz`
que contiene:

```
<nombre>.txt             — texto extraído
<nombre>.metadata.json   — metadatos del procesamiento
```

## Puertos y volúmenes

### docker-compose (API REST)

| Puerto | Descripción |
|---|---|
| `8000` | API REST (mapeado desde `PORT`) |

| Volumen | Modo | Descripción |
|---|---|---|
| `./data/input` | `ro` | Archivos de entrada (solo lectura) |
| `./data/output` | `rw` | Archivos de salida |

### docker run (CLI)

El CLI no usa volúmenes ni `docker cp` — transfiere archivos por
stdin/stdout, lo que lo hace compatible con Docker/Podman local y remoto.
El flujo interno de `scripts/shellscript/docker-run.sh` es:

1. Lee el archivo de entrada del host y lo envía por stdin al contenedor
2. El contenedor escribe stdin a un archivo temporal, ejecuta OCR, y
   envía el texto extraído por stdout
3. El host captura stdout y lo escribe al archivo de salida

## Troubleshooting

### El contenedor no inicia

```bash
# Ver logs detallados
docker compose -f containers/docker-compose.yml logs

# Reconstruir la imagen desde cero
docker compose -f containers/docker-compose.yml build --no-cache
```

### Error de autenticación (401)

Verificar que `AUTH_ENABLED` y `API_KEYS` en `.env` coincidan con el header
enviado:

```bash
# En .env
API_KEYS=mi-clave-secreta

# En la petición
curl -H "X-API-Key: mi-clave-secreta" ...
```

### Tesseract no encuentra idiomas

La imagen incluye `spa` y `eng`. Para otros idiomas, extender el Dockerfile:

```dockerfile
RUN apt-get install -y tesseract-ocr-fra  # francés
```

### PDF muy grande (>50 MB)

Aumentar `MAX_UPLOAD_BYTES` en `.env`:

```env
MAX_UPLOAD_BYTES=104857600  # 100 MB
```

### El OCR devuelve texto vacío o de baja calidad

- Aumentar `dpi` a 400 o 600 para mejor precisión.
- Especificar el idioma correcto: `lang=spa` (solo español).
- Usar `force_image=true` para forzar OCR en PDFs con capa de texto corrupta.
- Para imágenes, asegurarse de que tengan buena resolución y contraste.

### Error "statfs ... no such file or directory" con volúmenes

Ocurre cuando el contenedor corre en una máquina remota (Docker/Podman
remoto) y se intentan montar rutas del host local. `just docker-ocr`
usa stdin/stdout para transferir archivos, lo que funciona a través
de cualquier conexión Docker/Podman sin depender del filesystem del host.

## MCP Server

El contenedor expone un servidor MCP (Model Context Protocol) en el puerto
**9001** que permite a LLMs (Claude Desktop, Cursor, etc.) consumir las
capacidades de OCR. Soporta dos transportes:

| Transporte | Puerto | Uso |
|---|---|---|
| `stdio` | — (pipe) | Claude Desktop, Cursor en la misma maquina |
| `http` | `9001` | Clientes remotos via HTTP/SSE |

### Tools MCP expuestos

| Tool | Descripcion | Argumentos |
|---|---|---|
| `health_check` | Verificar estado del servicio | — |
| `ocr_document` | Extraer texto de PDF/imagen | `file_base64`, `filename`, `lang?`, `dpi?`, `validate?`, `force_image?` |
| `batch_ocr` | Procesar multiples archivos | `files[]`, `lang?`, `dpi?` |
| `validate_text` | Validar compatibilidad RAG | `text` |

### Configuracion para Claude Desktop

```json
{
  "mcpServers": {
    "ether-ocr": {
      "command": "python3",
      "args": ["-m", "ether_ocr_mcp.server", "--transport", "stdio"],
      "env": {
        "OCR_API_URL": "http://localhost:8000"
      }
    }
  }
}
```

### Cliente HTTP propio

```bash
# Iniciar MCP server en puerto 9001
python3 -m ether_ocr_mcp.server --transport http --port 9001

# Conectar desde cliente Python
python3 -m ether_ocr_mcp.client
# o con archivo
python3 -m ether_ocr_mcp.client documento.pdf
```

### Variables de entorno MCP

| Variable | Default | Descripcion |
|---|---|---|
| `MCP_TRANSPORT` | `stdio` | Transporte: `stdio` o `http` |
| `MCP_PORT` | `9001` | Puerto HTTP |
| `OCR_API_URL` | `http://localhost:8000` | URL de la API REST interna |
| `OCR_API_KEY` | *(vacio)* | API key (pendiente post-POC) |

## Shell interactivo en el contenedor

```bash
make docker-shell
# o
docker run --rm -it ether-ocr:latest /bin/bash
```

Dentro del contenedor se puede ejecutar cualquier comando del CLI:

```bash
python3 -m ether_ocr ocr /data/input/doc.pdf /data/output/out.txt
python3 -m ether_ocr prepare /data/input/doc.pdf /data/output/out.txt
python3 -m ether_ocr validate /data/output/out.txt
```
