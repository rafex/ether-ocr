#!/usr/bin/env python3
"""Build script — verifies the ether_ocr package can be imported and built."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    python_dir = repo_root / "python"
    src_dir = python_dir / "src"

    print(f"[build] Repository root: {repo_root}")
    print(f"[build] Python source:  {src_dir}")

    # Verify the package can be imported
    result = subprocess.run(
        [sys.executable, "-c", "from ether_ocr import prepare_document; print('OK: import successful')"],
        env={**__import__("os").environ, "PYTHONPATH": str(src_dir)},
        capture_output=True,
        text=True,
        cwd=str(repo_root),
    )

    if result.returncode != 0:
        print(f"[build] ERROR: Import failed\n{result.stderr}", file=sys.stderr)
        return 1

    print(result.stdout.strip())

    # Run quick syntax check on all Python files
    py_files = list(src_dir.rglob("*.py"))
    print(f"[build] Checking syntax of {len(py_files)} Python files...")
    for py_file in py_files:
        subprocess.run(
            [sys.executable, "-m", "py_compile", str(py_file)],
            check=True,
            cwd=str(src_dir),
        )
        print(f"  OK: {py_file.relative_to(src_dir)}")

    print("[build] Package verified successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
