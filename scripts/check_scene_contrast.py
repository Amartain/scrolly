"""Keep the finished-day ceremony card readable. Its colours are the same in every theme, so they
live in base.css (`--scene-*`) and are checked once here, by the rules of check_contrast.py."""

import sys

from check_contrast import DECLARATION, TOKENS, ratio

# Text on the lacquer card: body text 4.5:1, the big numerals and the title (display size) 3:1.
PAIRS = (
    ("--scene-card-ink", "--scene-card", 4.5),
    ("--scene-card-muted", "--scene-card", 4.5),
    ("--scene-card-muted", "--scene-card-raised", 4.5),
    ("--scene-mandate", "--scene-card-raised", 4.5),
    ("--scene-card-num", "--scene-card", 3.0),
    ("--scene-card-num", "--scene-card-raised", 3.0),
)


def main() -> int:
    values = dict(DECLARATION.findall((TOKENS / "base.css").read_text(encoding="utf-8")))
    found = []
    for token, surface, needed in PAIRS:
        if token not in values or surface not in values:
            found.append(f"base.css: {token} or {surface} is missing")
        elif (got := ratio(values[token], values[surface])) < needed:
            found.append(f"base.css: {token} on {surface} is {got:.2f}:1, needs {needed}:1")
    print("\n".join(found) or f"Scene contrast check passed ({len(PAIRS)} pairs).")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
