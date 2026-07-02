#!/usr/bin/env python3
"""Lint script — runs code quality checks on ether-ocr source and tests."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    python_dir = repo_root / "python"
    scripts_dir = repo_root / "scripts" / "python"

    src_dirs = [
        python_dir / "ether-core-ocr" / "src",
        python_dir / "ether-core-ocr" / "tests",
        python_dir / "ether-api-ocr" / "src",
        python_dir / "ether-api-ocr" / "tests",
        python_dir / "ether-cli-ocr" / "src",
        python_dir / "ether-mcp-ocr" / "src",
    ]
    dirs_arg = " ".join(str(d) for d in src_dirs if d.exists())

    errors = 0

    print("[lint] Running ruff check...")
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check"] + [str(d) for d in src_dirs if d.exists()] + [str(scripts_dir)],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        print("  OK: No issues found.")
    else:
        print(result.stdout or result.stderr)
        errors += 1

    print("[lint] Running ruff format check...")
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "format", "--check"] + [str(d) for d in src_dirs if d.exists()] + [str(scripts_dir)],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode == 0:
        print("  OK: Code is formatted.")
    else:
        print(result.stdout or result.stderr)
        errors += 1

    if errors > 0:
        print(f"\n[lint] {errors} check(s) failed.", file=sys.stderr)
        return 1

    print("\n[lint] All checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
