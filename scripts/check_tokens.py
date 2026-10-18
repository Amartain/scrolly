"""Keep components on design tokens (CLAUDE.md hard rules 2, 5, 6).

Scans frontend components, screens and icons. Token files, base.css and global.css are where raw
values live, so they are not scanned.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCANNED = ["components", "screens", "icons"]
MANDATE_ALLOWED = {"MandateMark.svelte"}  # components that may use --mandate

COLOR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgb|rgba|hsl|hsla)\(")
PX = re.compile(r"\d\s*px\b")
TOKEN_ONLY = re.compile(
    r"^\s*(padding[\w-]*|margin[\w-]*|gap|row-gap|column-gap|font-size|box-shadow)\s*:\s*([^;]+);"
)
ZERO_OK = {"0", "auto", "none"}


def problems(path: Path) -> list[str]:
    found = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        where = f"{path.relative_to(ROOT)}:{number}"
        if COLOR.search(line):
            found.append(f"{where}: raw color, use a token")
        if PX.search(line):
            found.append(f"{where}: px value, use a token (rem scale)")
        match = TOKEN_ONLY.match(line)
        if match:
            value = match.group(2).strip()
            if value not in ZERO_OK and not value.startswith("var(--"):
                found.append(f"{where}: {match.group(1)} must be a token, got '{value}'")
        if "--mandate" in line and path.name not in MANDATE_ALLOWED:
            found.append(f"{where}: --mandate is for Heavenly Mandates only")
    return found


def main() -> int:
    base = ROOT / "frontend" / "src"
    files = [
        path
        for folder in SCANNED
        for path in (base / folder).rglob("*")
        if path.suffix in {".svelte", ".css", ".ts"}
    ]
    found = [issue for path in sorted(files) for issue in problems(path)]
    print("\n".join(found) or f"Token check passed ({len(files)} files).")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
