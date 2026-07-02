#!/usr/bin/env python3
"""Build script — verifies ether-ocr packages can be imported."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_IMPORT_CHECK = """
from ether_ocr_core import ocr_document, prepare_document, validate_plain_text
from ether_ocr_api import create_app
from ether_ocr_cli.cli import main as cli_main
from ether_ocr_mcp.server import main as mcp_main
print('ALL packages imported OK')
"""


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    print(f"[build] Repository root: {repo_root}")

    result = subprocess.run(
        [sys.executable, "-c", _IMPORT_CHECK],
        capture_output=True,
        text=True,
        cwd=str(repo_root),
        check=False,
    )

    if result.returncode != 0:
        print(f"[build] ERROR: Import failed\n{result.stderr}", file=sys.stderr)
        return 1

    print(result.stdout.strip())

    # Syntax check on all source files
    src_dirs = [
        repo_root / "python" / "ether-core-ocr" / "src",
        repo_root / "python" / "ether-api-ocr" / "src",
        repo_root / "python" / "ether-cli-ocr" / "src",
        repo_root / "python" / "ether-mcp-ocr" / "src",
    ]
    for src_dir in src_dirs:
        if not src_dir.exists():
            continue
        py_files = list(src_dir.rglob("*.py"))
        print(f"[build] Syntax check: {len(py_files)} files in {src_dir.relative_to(repo_root)}")
        for py_file in py_files:
            subprocess.run(
                [sys.executable, "-m", "py_compile", str(py_file)],
                check=True,
                cwd=str(src_dir),
            )
            print(f"  OK: {py_file.relative_to(src_dir)}")

    print("[build] All packages verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
