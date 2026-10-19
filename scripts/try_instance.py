"""Run Scrolly on a scratch data folder, next to the real one.

  poe try-mine   ~/scrolly-mine  port 4757  your prototype data, imported once on the first run
  poe try-blank  ~/scrolly-blank port 4767  always starts empty: the folder is wiped first

Each folder has its own lock file, so both can run together. ~/.scrolly is never touched.
It serves the last built frontend (`poe build` or `poe check` builds it).
"""

import argparse
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROTOTYPE_DATA = ROOT / "prototype" / "data"
INSTANCES = {
    "mine": (Path.home() / "scrolly-mine", 4757),
    "blank": (Path.home() / "scrolly-blank", 4767),
}


def import_prototype_data() -> None:
    """Merge the prototype JSON files, then the Discord boards, into the (new) database."""
    from scrolly.clock import SystemClock
    from scrolly.config import data_dir, db_path
    from scrolly.io.importers import parse_upload
    from scrolly.services.importing import ImportService
    from scrolly.storage.migrate import upgrade_to_head
    from scrolly.storage.store import SqliteStores, make_engine

    upgrade_to_head(db_path(), data_dir() / "backups")
    stores = SqliteStores(make_engine(db_path()))
    files = sorted(PROTOTYPE_DATA.glob("*.json")) + sorted(PROTOTYPE_DATA.glob("**/*.md"))
    for path in files:
        with stores() as store:
            batch = parse_upload(path.name, path.read_bytes())
            summary = ImportService(store, SystemClock()).merge(batch)
        print(f"imported {path.name}: {summary}")


def wipe(home: Path) -> bool:
    """Empty the folder so the next start is a first run. False if something still holds it."""
    try:
        shutil.rmtree(home)
    except FileNotFoundError:
        return True
    except OSError as error:
        print(f"Could not wipe {home}: {error}", file=sys.stderr)
        print("Close the running try-blank first, then run it again.", file=sys.stderr)
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("which", choices=INSTANCES)
    args = parser.parse_args()

    home, port = INSTANCES[args.which]
    if args.which == "blank" and not wipe(home):
        return 1
    os.environ["SCROLLY_HOME"] = str(home)
    home.mkdir(parents=True, exist_ok=True)

    if args.which == "mine" and not (home / "scrolly.db").exists():
        import_prototype_data()

    from scrolly import cli

    sys.argv = ["scrolly", "--port", str(port)]
    cli.main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
