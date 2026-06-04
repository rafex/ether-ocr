#!/usr/bin/env python3
"""API script — starts the ether-ocr REST API server."""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    src_dir = repo_root / "python" / "src"
    sys.path.insert(0, str(src_dir))

    from ether_ocr.api.server import main as run_server

    run_server()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
