#!/usr/bin/env python3
"""Test script — discovers and runs all unit tests for ether_ocr."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    src_dir = repo_root / "python" / "src"
    tests_dir = repo_root / "python" / "tests"

    print(f"[test] Source:  {src_dir}")
    print(f"[test] Tests:   {tests_dir}")

    if not list(tests_dir.glob("test_*.py")):
        print("[test] WARNING: No test files found in python/tests/", file=sys.stderr)

    result = subprocess.run(
        [
            sys.executable,
            "-m", "unittest",
            "discover",
            "-s", str(tests_dir),
            "-v",
        ],
        env={**__import__("os").environ, "PYTHONPATH": str(src_dir)},
        cwd=str(repo_root),
        capture_output=False,
        text=True,
    )

    if result.returncode == 0:
        print("\n[test] All tests passed.")
    else:
        print(f"\n[test] Tests failed with exit code {result.returncode}.", file=sys.stderr)

    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
