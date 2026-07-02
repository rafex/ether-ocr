#!/usr/bin/env python3
"""Test script — discovers and runs all unit tests for ether-ocr packages."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    python_dir = repo_root / "python"

    test_dirs = [
        python_dir / "ether-core-ocr" / "tests",
        python_dir / "ether-api-ocr" / "tests",
    ]

    exit_code = 0
    for tests_dir in test_dirs:
        if not tests_dir.exists() or not list(tests_dir.glob("test_*.py")):
            print(f"[test] SKIP: {tests_dir.relative_to(repo_root)} — no tests")
            continue

        print(f"[test] Running tests in {tests_dir.relative_to(repo_root)}")
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", str(tests_dir), "-v"],
            cwd=str(repo_root),
            capture_output=False,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            exit_code = result.returncode

    if exit_code == 0:
        print("\n[test] All tests passed.")
    else:
        print(f"\n[test] Tests failed with exit code {exit_code}.", file=sys.stderr)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
