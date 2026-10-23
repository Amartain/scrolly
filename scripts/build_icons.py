"""Make the executable's icons (packaging/scrolly.ico and .icns) from packaging/scrolly-icon.png.

Run after changing the icon: `uv run python scripts/build_icons.py`. The PNG is the 1024 px
rendering of packaging/scrolly-icon.svg.
"""

import sys
from pathlib import Path

from PIL import Image

PACKAGING = Path(__file__).resolve().parent.parent / "packaging"
ICO_SIZES = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


def main() -> int:
    source = Image.open(PACKAGING / "scrolly-icon.png").convert("RGBA")
    source.save(PACKAGING / "scrolly.ico", sizes=ICO_SIZES)
    source.save(PACKAGING / "scrolly.icns")
    print("Wrote scrolly.ico and scrolly.icns")
    return 0


if __name__ == "__main__":
    sys.exit(main())
