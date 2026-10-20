import importlib.util
from pathlib import Path
from types import ModuleType

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "code_map.py"


def load_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("code_map", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_module_with_a_docstring_uses_its_first_line() -> None:
    code_map = load_script()
    assert code_map.python_summary('"""Pure timer rules.\n\nMore."""\n\ndef start(): ...\n') == (
        "Pure timer rules."
    )


def test_module_without_a_docstring_still_gets_its_public_names() -> None:
    code_map = load_script()
    source = "def start(): ...\ndef _hidden(): ...\nclass Timer: ...\n"
    assert code_map.python_summary(source) == "start, Timer"


def test_typescript_and_svelte_fall_back_to_exports_and_components() -> None:
    code_map = load_script()
    assert code_map.typescript_summary("/**\n * The chime.\n */\nexport function play() {}\n") == (
        "The chime."
    )
    assert code_map.typescript_summary("export async function a() {}\nexport const b = 1\n") == (
        "a, b"
    )
    assert code_map.svelte_summary(
        "<script>\n  import Panel from '../Panel.svelte';\n</script>"
    ) == ("uses Panel")


def test_check_fails_on_a_stale_map(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    code_map = load_script()
    stale = tmp_path / "docs" / "code-map.md"
    stale.parent.mkdir()
    stale.write_text("old\n", encoding="utf-8")
    monkeypatch.setattr(code_map, "OUT", stale)
    monkeypatch.setattr("sys.argv", ["code_map.py", "--check"])
    assert code_map.main() == 1
    stale.write_text(code_map.build_map(), encoding="utf-8")
    assert code_map.main() == 0
