from fastapi.testclient import TestClient


def test_the_view_says_who_is_a_player_and_what_can_be_worn(client: TestClient) -> None:
    player = client.get("/api/view").json()["player"]
    assert player["is_player"] is False
    assert player["rewarded"] is False
    assert player["colours"][0] == "system-blue"
    assert "crimson" in player["colours"]


def test_yes_rewards_the_player_once_and_keeps_the_choice_after(client: TestClient) -> None:
    player = client.post("/api/player/accept").json()["player"]
    assert player["is_player"] and player["rewarded"]
    assert (player["robe"], player["glow"], player["glow_on"]) == (
        "system-blue",
        "system-blue",
        True,
    )

    aura = {"robe": "jade", "glow": None, "glow_on": False}
    assert client.put("/api/player/aura", json=aura).json()["player"]["robe"] == "jade"
    again = client.post("/api/player/accept").json()["player"]
    assert (again["robe"], again["glow"], again["glow_on"]) == ("jade", None, False)


def test_an_aura_is_refused_before_the_arise_window(client: TestClient) -> None:
    reply = client.put("/api/player/aura", json={"robe": "gold", "glow": None, "glow_on": True})
    assert reply.status_code == 422


def test_an_unknown_colour_is_refused(client: TestClient) -> None:
    client.post("/api/player/accept")
    reply = client.put("/api/player/aura", json={"robe": "white", "glow": None, "glow_on": True})
    assert reply.status_code == 422
