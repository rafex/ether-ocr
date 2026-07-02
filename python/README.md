# python/ — Ether OCR packages

Cuatro paquetes Python con gestion UV independiente:

| Paquete | Descripcion |
|---|---|
| `ether-core-ocr/` | Motor OCR y dominio compartido (pipeline, extractor, limpieza, validacion) |
| `ether-api-ocr/` | API REST con FastAPI |
| `ether-cli-ocr/` | CLI para OCR desde terminal |
| `ether-mcp-ocr/` | MCP Server para exponer OCR a LLMs (Claude, Cursor, etc.) |

## Instalacion

```bash
pip install -e python/ether-core-ocr/
pip install -e python/ether-api-ocr/
pip install -e python/ether-cli-ocr/
pip install -e python/ether-mcp-ocr/
```

## Entry points

| Comando | Paquete |
|---|---|
| `ether-ocr` | CLI |
| `ether-ocr-api` | API server |
| `ether-ocr-mcp` | MCP server |
