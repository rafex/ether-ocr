"""Allow python3 -m ether_ocr_cli to run the CLI."""
from ether_ocr_cli.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
