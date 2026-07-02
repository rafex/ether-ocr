"""MCP server entry point — exposes ether-ocr capabilities to LLMs.

Usage:
    # stdio transport (for Claude Desktop, Cursor, etc.)
    python3 -m ether_ocr_mcp.server --transport stdio

    # HTTP/SSE transport (for custom clients)
    python3 -m ether_ocr_mcp.server --transport http --port 9001
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from ether_ocr_mcp.tools import call_health_check, call_ocr_document, call_batch_ocr, call_validate_text

mcp_server = Server("ether-ocr")


@mcp_server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="health_check",
            description="Verify the ether-ocr API is healthy and responding.",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="ocr_document",
            description=(
                "Extract text from a PDF or image file using OCR."
                " The file must be provided as a base64-encoded string."
                " Returns cleaned UTF-8 text with metadata."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_base64": {
                        "type": "string",
                        "description": "Base64-encoded file content.",
                    },
                    "filename": {
                        "type": "string",
                        "description": "Original filename with extension.",
                    },
                    "lang": {
                        "type": "string",
                        "description": "Tesseract language(s).",
                        "default": "spa+eng",
                    },
                    "dpi": {
                        "type": "integer",
                        "description": "DPI for PDF-to-image conversion.",
                        "default": 300,
                    },
                    "validate": {
                        "type": "boolean",
                        "description": "Run RAG validation.",
                        "default": True,
                    },
                    "force_image": {
                        "type": "boolean",
                        "description": "Force image mode.",
                        "default": False,
                    },
                },
                "required": ["file_base64", "filename"],
            },
        ),
        Tool(
            name="batch_ocr",
            description="Process multiple files through the OCR pipeline at once.",
            inputSchema={
                "type": "object",
                "properties": {
                    "files": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "base64": {"type": "string"},
                                "filename": {"type": "string"},
                            },
                            "required": ["base64", "filename"],
                        },
                        "description": "List of files to process.",
                    },
                    "lang": {
                        "type": "string",
                        "default": "spa+eng",
                    },
                    "dpi": {
                        "type": "integer",
                        "default": 300,
                    },
                },
                "required": ["files"],
            },
        ),
        Tool(
            name="validate_text",
            description="Validate a text string for RAG compatibility.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to validate.",
                    },
                },
                "required": ["text"],
            },
        ),
    ]


@mcp_server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    if name == "health_check":
        status = await call_health_check()
        return [TextContent(type="text", text=status)]

    if name == "ocr_document":
        result = await call_ocr_document(
            file_base64=arguments["file_base64"],
            filename=arguments["filename"],
            lang=arguments.get("lang", "spa+eng"),
            dpi=arguments.get("dpi", 300),
            validate=arguments.get("validate", True),
            force_image=arguments.get("force_image", False),
        )
        return [TextContent(type="text", text=result)]

    if name == "batch_ocr":
        result = await call_batch_ocr(
            files=arguments["files"],
            lang=arguments.get("lang", "spa+eng"),
            dpi=arguments.get("dpi", 300),
        )
        return [TextContent(type="text", text=result)]

    if name == "validate_text":
        result = await call_validate_text(arguments["text"])
        return [TextContent(type="text", text=result)]

    raise ValueError(f"Unknown tool: {name}")


async def run_stdio() -> None:
    """Run MCP server on stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options(),
        )


async def run_http(port: int) -> None:
    """Run MCP server on HTTP/SSE transport."""
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.routing import Route

    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await mcp_server.run(
                streams[0],
                streams[1],
                mcp_server.create_initialization_options(),
            )

    app = Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse),
            Route("/messages/", endpoint=sse.handle_post_message),
        ],
    )

    import uvicorn

    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


def main() -> None:
    parser = argparse.ArgumentParser(description="ether-ocr MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http"],
        default=os.getenv("MCP_TRANSPORT", "stdio"),
        help="Transport protocol (default: stdio)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("MCP_PORT", "9001")),
        help="HTTP port (default: 9001)",
    )
    args = parser.parse_args()

    if args.transport == "stdio":
        asyncio.run(run_stdio())
    else:
        asyncio.run(run_http(args.port))


if __name__ == "__main__":
    main()
