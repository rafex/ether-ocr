#!/usr/bin/env python3
"""Validador de integracion para el MCP server de ether-ocr.

Lanza el MCP server en modo stdio, conecta un cliente y verifica
que los 4 tools esten registrados y respondan correctamente.

Uso:
  python3 validate_mcp.py
  OCR_API_URL=http://192.168.1.100:8000 python3 validate_mcp.py
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession

REPO_ROOT = Path(__file__).parent.parent
MCP_SRC = REPO_ROOT / "python" / "ether-mcp-ocr" / "src"

os.environ.setdefault("OCR_API_URL", "http://localhost:8000")
os.environ.setdefault("OCR_API_KEY", os.environ.get("OCR_API_KEY", ""))

passed = 0
failed = 0


def _ok(name: str) -> None:
    global passed
    passed += 1
    print(f"  PASS  {name}")


def _fail(name: str, detail: str) -> None:
    global failed
    failed += 1
    print(f"  FAIL  {name}: {detail}")


async def test_tools_registered(session: ClientSession) -> None:
    name = "tools registrados"
    try:
        tools_result = await session.list_tools()
        tool_names = {t.name for t in tools_result.tools}
        expected = {"health_check", "ocr_document", "batch_ocr", "validate_text"}
        if expected.issubset(tool_names):
            _ok(name)
        else:
            missing = expected - tool_names
            _fail(name, f"faltan tools: {missing}")
    except Exception as exc:
        _fail(name, str(exc))


async def test_health_check(session: ClientSession) -> None:
    name = "tool: health_check"
    try:
        result = await session.call_tool("health_check", {})
        text = result.content[0].text
        data = json.loads(text)
        if data.get("status") == "ok":
            _ok(name)
        else:
            _fail(name, f"status={data.get('status')}")
    except Exception as exc:
        _fail(name, str(exc))


async def test_validate_text(session: ClientSession) -> None:
    name = "tool: validate_text"
    try:
        result = await session.call_tool(
            "validate_text",
            {"text": "Texto UTF-8 limpio. Sin Markdown ni HTML."},
        )
        text = result.content[0].text
        data = json.loads(text)
        if data.get("valid") is True:
            _ok(name)
        else:
            _fail(name, f"valid={data.get('valid')}")
    except Exception as exc:
        _fail(name, str(exc))


async def main() -> int:
    print(f"\nether-ocr MCP validator")
    print(f"  API:  {os.environ['OCR_API_URL']}")
    print()

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "ether_ocr_mcp.server", "--transport", "stdio"],
        env={
            **os.environ,
            "PYTHONPATH": str(MCP_SRC),
        },
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                await test_tools_registered(session)
                await test_validate_text(session)
                await test_health_check(session)
    except Exception as exc:
        _fail("conexion MCP", str(exc))

    print(f"\n  Resultado: {passed} OK, {failed} FAIL")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
