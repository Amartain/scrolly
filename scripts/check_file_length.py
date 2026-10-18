"""Fail when a hand-written code file is longer than 200 lines (CLAUDE.md hard rule 12)."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_LINES = 200
EXTENSIONS = {".py", ".ts", ".svelte", ".css", ".js"}
SKIP_DIRS = {
    ".venv", "node_modules", ".git", "prototype", "docs", "static", "dist",
    "test-results", "playwright-report", "versions", "__pycache__", ".mypy_cache",
    ".ruff_cache", ".pytest_cache", ".hypothesis", ".claude",
}  # fmt: skip
GENERATED = {"api-types.ts"}


def code_files() -> list[Path]:
    return [
        path
        for path in ROOT.rglob("*")
        if path.suffix in EXTENSIONS
        and path.name not in GENERATED
        and not SKIP_DIRS.intersection(path.relative_to(ROOT).parts)
    ]


def main() -> int:
    too_long = []
    for path in code_files():
        count = len(path.read_text(encoding="utf-8").splitlines())
        if count > MAX_LINES:
            too_long.append(f"{path.relative_to(ROOT)}: {count} lines (max {MAX_LINES})")
    print("\n".join(too_long) or f"All code files are within {MAX_LINES} lines.")
    return 1 if too_long else 0


if __name__ == "__main__":
    sys.exit(main())
