"""MCP client example — demonstrates connecting to the ether-ocr MCP server.

Usage:
    python3 -m ether_ocr_mcp.client

    # Via HTTP:
    OCR_MCP_URL=http://localhost:9001 python3 -m ether_ocr_mcp.client

    # With a file:
    python3 -m ether_ocr_mcp.client path/to/document.pdf
"""

from __future__ import annotations

import asyncio
import base64
import os
import sys
from pathlib import Path

from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

URL = os.getenv("OCR_MCP_URL", "")


async def run_stdio(sample_file: str | None = None) -> int:
    server_params = StdioServerParameters(
        command="python3",
        args=["-m", "ether_ocr_mcp.server", "--transport", "stdio"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print(f"Tools disponibles: {[t.name for t in tools.tools]}")

            if sample_file:
                data = Path(sample_file).read_bytes()
                b64 = base64.b64encode(data).decode("utf-8")
                filename = Path(sample_file).name

                result = await session.call_tool(
                    "ocr_document",
                    {"file_base64": b64, "filename": filename},
                )
                for content in result.content:
                    print(content.text)
            else:
                result = await session.call_tool("health_check", {})
                for content in result.content:
                    print(content.text)

    return 0


async def run_http(sample_file: str | None = None) -> int:
    url = URL or "http://localhost:9001"
    print(f"Conectando a MCP server en {url}/sse ...")

    async with sse_client(f"{url}/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print(f"Tools disponibles: {[t.name for t in tools.tools]}")

            if sample_file:
                data = Path(sample_file).read_bytes()
                b64 = base64.b64encode(data).decode("utf-8")
                filename = Path(sample_file).name

                result = await session.call_tool(
                    "ocr_document",
                    {"file_base64": b64, "filename": filename},
                )
                for content in result.content:
                    print(content.text)
            else:
                result = await session.call_tool("health_check", {})
                for content in result.content:
                    print(content.text)

    return 0


def main() -> None:
    sample_file = sys.argv[1] if len(sys.argv) > 1 else None
    if URL:
        sys.exit(asyncio.run(run_http(sample_file)))
    else:
        sys.exit(asyncio.run(run_stdio(sample_file)))


if __name__ == "__main__":
    main()
