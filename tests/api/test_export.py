import csv
import io
import zipfile

from fastapi.testclient import TestClient


def _zip(client: TestClient) -> zipfile.ZipFile:
    reply = client.get("/api/export")
    assert reply.status_code == 200
    return zipfile.ZipFile(io.BytesIO(reply.content))


def _table(archive: zipfile.ZipFile, name: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(archive.read(f"{name}.csv").decode("utf-8"))))


def test_backup_is_a_timestamped_zip_with_one_csv_per_table(client: TestClient) -> None:
    reply = client.get("/api/export")
    assert reply.headers["content-type"] == "application/zip"
    assert 'filename="scrolly-20261018-131200.zip"' in reply.headers["content-disposition"]
    names = set(zipfile.ZipFile(io.BytesIO(reply.content)).namelist())
    assert {"trial.csv", "horizon_item.csv", "art.csv", "day.csv", "setting.csv"} <= names
    assert "planning_draft.csv" in names


def test_the_trial_table_carries_every_column_including_art_kind(client: TestClient) -> None:
    client.post("/api/planning/start")
    client.put("/api/planning/text", json={"text": "Write the report\n日落"})
    client.post("/api/planning/proceed")
    client.post("/api/planning/seal")
    trials = _table(_zip(client), "trial")
    assert {t["title"] for t in trials} == {"Write the report", "日落"}
    for column in ("art_kind", "qi_actual", "timer_accumulated_s", "realm_id", "created_at"):
        assert column in trials[0]
    assert trials[0]["realm_id"] == "daily"
    assert trials[0]["is_mandate"] in {"true", "false"}


def test_worked_time_and_settings_are_exported_too(client: TestClient) -> None:
    client.put("/api/sunset", json={"at": "20:30"})
    archive = _zip(client)
    assert "worked_s" in archive.read("horizon_item.csv").decode().splitlines()[0]
    keys = {row["key"] for row in _table(archive, "setting")}
    assert "sunset" in keys
