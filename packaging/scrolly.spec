# PyInstaller recipe for the Scrolly executable: `uv run poe exe` (scripts/build_exe.py) runs it.
# One folder, not one file: it starts faster and antivirus tools flag it less. On macOS the folder
# goes into Scrolly.app. The frontend must be built first (src/scrolly/static).
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

HERE = Path(SPECPATH)  # noqa: F821 - given by PyInstaller

# Read from disk at run time: the built frontend, the content files and the Alembic migrations
# (Alembic loads them as files, so the .py files go in as data too).
datas = collect_data_files(
    "scrolly",
    includes=["static/**", "content/**", "storage/migrations/**", "py.typed"],
    include_py_files=True,
) + [
    (str(HERE / "scrolly-icon.png"), "."),  # the small window's own icon
    (str(HERE.parent / "LICENSE"), "."),
    (str(HERE.parent / "THIRD_PARTY_NOTICES.md"), "."),
]
hiddenimports = collect_submodules("uvicorn") + collect_submodules("alembic")
icon = str(HERE / ("scrolly.icns" if sys.platform == "darwin" else "scrolly.ico"))

a = Analysis(  # noqa: F821
    [str(HERE / "scrolly_app.py")],
    datas=datas,
    hiddenimports=hiddenimports,
    # Dev tools, and optional imports Scrolly never uses (Pillow is only for scripts/build_icons.py).
    excludes=["pytest", "hypothesis", "mypy", "ruff", "PIL", "yaml"],
)
pyz = PYZ(a.pure)  # noqa: F821
exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    exclude_binaries=True,
    name="Scrolly",
    console=False,
    icon=icon,
)
coll = COLLECT(exe, a.binaries, a.datas, name="Scrolly")  # noqa: F821

if sys.platform == "darwin":
    app = BUNDLE(  # noqa: F821
        coll,
        name="Scrolly.app",
        icon=icon,
        bundle_identifier="io.github.amartain.scrolly",
        info_plist={"NSHighResolutionCapable": True},
    )
