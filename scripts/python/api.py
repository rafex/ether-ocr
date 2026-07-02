#!/usr/bin/env python3
"""API script — starts the ether-ocr REST API server."""

from __future__ import annotations

import sys


def main() -> int:
    from ether_ocr_api.server import main as run_server

    run_server()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
