"""Generate frontend/src/lib/api-types.ts from the API's OpenAPI schema.

`--check` fails when the committed file is out of date instead of writing it.
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import cast

from scrolly.api.app import create_app
from scrolly.clock import SystemClock
from scrolly.ports import StoreFactory

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"
TARGET = FRONTEND / "src" / "lib" / "api-types.ts"


def generate(output: Path) -> None:
    app = create_app(SystemClock(), cast(StoreFactory, None))
    with tempfile.TemporaryDirectory() as folder:
        schema = Path(folder) / "openapi.json"
        schema.write_text(json.dumps(app.openapi(), indent=2, sort_keys=True), encoding="utf-8")
        npx = shutil.which("npx") or "npx"
        subprocess.run(
            [npx, "openapi-typescript", str(schema), "-o", str(output)],
            cwd=FRONTEND,
            check=True,
            capture_output=True,
        )


def main() -> int:
    if "--check" not in sys.argv:
        generate(TARGET)
        print(f"Wrote {TARGET.relative_to(ROOT)}")
        return 0
    with tempfile.TemporaryDirectory() as folder:
        fresh = Path(folder) / "api-types.ts"
        generate(fresh)
        current = TARGET.read_text(encoding="utf-8") if TARGET.exists() else ""
        if fresh.read_text(encoding="utf-8") != current:
            print("api-types.ts is stale. Run: uv run poe types")
            return 1
    print("api-types.ts is up to date.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
