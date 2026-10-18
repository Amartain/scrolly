"""Turn the header illustrations in docs/references into web-sized WebP files."""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SOURCES = {
    "serene-day": "serene_peak_daylight.jpg",
    "serene-dusk": "serene_peak_dusk.jpg",
    "pavilion": "hidden_pavilion.jpg",
}
WIDTH = 2880


def main() -> None:
    target = ROOT / "frontend" / "src" / "assets" / "headers"
    target.mkdir(parents=True, exist_ok=True)
    for name, source in SOURCES.items():
        image = Image.open(ROOT / "docs" / "references" / source).convert("RGB")
        height = round(image.height * WIDTH / image.width)
        image.resize((WIDTH, height), Image.Resampling.LANCZOS).save(
            target / f"{name}.webp", quality=80, method=6
        )
        print(f"{name}.webp {WIDTH}x{height}")


if __name__ == "__main__":
    main()
