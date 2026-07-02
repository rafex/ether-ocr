# ether-mcp-ocr

MCP Server que expone las capacidades de OCR de ether-ocr a LLMs
via Model Context Protocol.

## Instalacion

```bash
pip install -e python/ether-mcp-ocr/
```

## Transportes

### stdio (Claude Desktop, Cursor)

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

### HTTP/SSE (clientes propios)

```bash
python3 -m ether_ocr_mcp.server --transport http --port 9001
```

## Tools MCP

| Tool | Descripcion |
|---|---|
| `health_check` | Verificar estado del servicio |
| `ocr_document` | Extraer texto de PDF/imagen (base64) |
| `batch_ocr` | Procesar multiples archivos |
| `validate_text` | Validar compatibilidad RAG |

## Configuracion

| Variable | Default | Descripcion |
|---|---|---|
| `OCR_API_URL` | `http://localhost:8000` | URL de la API REST |
| `OCR_API_KEY` | *(vacio)* | API key (pendiente post-POC) |
| `MCP_TRANSPORT` | `stdio` | Transporte: stdio o http |
| `MCP_PORT` | `9001` | Puerto HTTP |
