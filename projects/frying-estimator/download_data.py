"""Prepare this project's external inputs; see DATA.md."""

import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
ROOT = next(
    parent for parent in PROJECT.parents if (parent / "_support/downloads.py").is_file()
)
sys.path.insert(0, str(ROOT))
from _support.downloads import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(PROJECT))
