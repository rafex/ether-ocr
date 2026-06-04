#!/usr/bin/env python3
"""Lint script — runs code quality checks on ether_ocr source and tests."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    src_dir = repo_root / "python" / "src"
    tests_dir = repo_root / "python" / "tests"
    scripts_dir = repo_root / "scripts" / "python"

    errors = 0

    # ── ruff check ───────────────────────────────────
    print("[lint] Running ruff check...")
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "check", str(src_dir), str(tests_dir), str(scripts_dir)],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print("  OK: No issues found.")
    else:
        print(result.stdout or result.stderr)
        errors += 1

    # ── ruff format check ────────────────────────────
    print("[lint] Running ruff format check...")
    result = subprocess.run(
        [sys.executable, "-m", "ruff", "format", "--check", str(src_dir), str(tests_dir), str(scripts_dir)],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print("  OK: Code is formatted.")
    else:
        print(result.stdout or result.stderr)
        errors += 1

    # ── mypy (optional) ───────────────────────────────
    print("[lint] Running mypy type check...")
    result = subprocess.run(
        [sys.executable, "-m", "mypy", str(src_dir), "--ignore-missing-imports"],
        cwd=str(repo_root),
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print("  OK: No type errors.")
    else:
        reported = (result.stdout or "") + (result.stderr or "")
        if reported.strip():
            print(reported)
        else:
            print("  OK: No type errors.")

    if errors > 0:
        print(f"\n[lint] {errors} check(s) failed.", file=sys.stderr)
        return 1

    print("\n[lint] All checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
