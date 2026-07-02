# ether-ocr

Motor OCR y preparador de documentos para convertir PDFs (con o sin capa
de texto) e imágenes a texto plano UTF-8 listo para RAG.

## Inicio rápido

```bash
# Instalar dependencias del sistema
bash scripts/shellscript/setup.sh

# O usar Docker/Podman (no requiere instalar nada en el host)
make docker-build
just docker-ocr documento.pdf salida.txt
```

## API REST

Servicio HTTP con endpoints de OCR, preparación y validación.

| Método | Endpoint | Descripción | Auth |
|---|---|---|---|
| `GET` | `/api/v1/health` | Health check | No |
| `POST` | `/api/v1/ocr` | Extraer texto de PDF/imagen | Sí |
| `POST` | `/api/v1/ocr/batch` | Procesar múltiples archivos | Sí |
| `POST` | `/api/v1/prepare` | Preparar documento (Poppler) | Sí |
| `POST` | `/api/v1/validate` | Validar texto para RAG | Sí |

Especificación completa: [`openapi/ocr-api.yaml`](openapi/ocr-api.yaml)

Swagger UI disponible en `/docs` cuando el servicio está corriendo.

```bash
# Iniciar API local
make api

# Usar la API
curl -X POST http://localhost:8000/api/v1/ocr \
  -H "X-API-Key: dev-key-ether-ocr" \
  -F "file=@documento.pdf"
```

## MCP Server

Servidor Model Context Protocol que expone capacidades OCR a LLMs
(Claude Desktop, Cursor, etc.).

| Tool | Descripción |
|---|---|
| `health_check` | Verificar estado del servicio |
| `ocr_document` | Extraer texto de PDF/imagen (base64) |
| `batch_ocr` | Procesar múltiples archivos |
| `validate_text` | Validar texto para RAG |

Especificación completa: [`openapi/ocr-mcp.yaml`](openapi/ocr-mcp.yaml)

```bash
# MCP via stdio (Claude Desktop, Cursor)
make mcp

# MCP via HTTP (:9001)
make mcp-http
```

### Configuración Claude Desktop

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

## Docker / Podman

```bash
# Build de la imagen (Python 3.11 + Poppler + Tesseract spa/eng)
make docker-build

# Levantar API + MCP con docker-compose / podman-compose
make docker-up

# OCR dentro del contenedor
just docker-ocr escaneado.pdf salida.txt

# Shell interactivo
make docker-shell
```

Documentación detallada: [`docs/ocr-contenedores.md`](docs/ocr-contenedores.md)

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
PYTHONPATH=python/ether-core-ocr/src python3 -m ether_ocr ocr escaneado.pdf salida.txt

# Preparar PDF con capa de texto (Poppler)
PYTHONPATH=python/ether-core-ocr/src python3 -m ether_ocr prepare entrada.pdf salida.txt

# Validar texto para RAG
PYTHONPATH=python/ether-core-ocr/src python3 -m ether_ocr validate salida.txt

# Tests
make test
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
├── python/
│   ├── ether-core-ocr/   ← Paquete core (pipeline, ocr, cleaner, validator)
│   ├── ether-api-ocr/    ← API REST (FastAPI + uvicorn)
│   ├── ether-cli-ocr/    ← CLI (click)
│   └── ether-mcp-ocr/    ← MCP server (tools + SSE transport)
├── openapi/
│   ├── ocr-api.yaml      ← Especificación OpenAPI de la REST API
│   └── ocr-mcp.yaml      ← Especificación del MCP server
├── containers/           ← Dockerfile + docker-compose
├── scripts/              ← Scripts orquestables
│   ├── python/           ← Scripts Python (build, test, ocr, lint)
│   ├── shellscript/      ← Shell scripts (docker, setup)
│   ├── mk/               ← Includes de Makefile
│   └── just/             ← Includes de Justfile
├── docs/                 ← Documentación
├── tests/                ← Tests e2e y generación de PDFs
├── Makefile              ← Build orchestrator
├── Justfile              ← Task runner
└── spec-native/          ← Contexto SpecNative del proyecto
```

## OpenAPI

Las especificaciones OpenAPI 3.0 están en [`openapi/`](openapi/):

- [`ocr-api.yaml`](openapi/ocr-api.yaml) — REST API: endpoints, schemas, auth, rate limiting
- [`ocr-mcp.yaml`](openapi/ocr-mcp.yaml) — MCP Server: SSE transport, JSON-RPC tools, configuración

Se pueden visualizar con [Swagger Editor](https://editor.swagger.io) o cualquier
herramienta compatible con OpenAPI 3.0.

## Roadmap

- ✅ Preparador PDF→texto con Poppler
- ✅ Motor OCR con Tesseract
- ✅ API REST (FastAPI) con auth, rate limiting, batch
- ✅ MCP Server para LLMs
- ✅ Docker/Podman con API + MCP
- ⏳ Preprocesamiento de imagen (deskew, thresholding)
- ⏳ Migración a Rust
