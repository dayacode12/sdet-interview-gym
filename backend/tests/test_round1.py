"""Round 1 playbook: content integrity and evidence discipline."""
from __future__ import annotations

EVIDENCE = {"official", "jd", "reported", "standard"}
SOURCE_TYPES = {"official", "brief", "standard"}


def test_round1_payload_shape(client):
    resp = client.get("/api/round1")
    assert resp.status_code == 200
    body = resp.json()

    assert body["title"] == "Round 1 Playbook"
    assert body["question_count"] == sum(len(s["questions"]) for s in body["sections"])
    assert body["question_count"] >= 20
    assert [s["id"] for s in body["sections"]] == [
        "java-automation",
        "api-db",
        "iam-security",
    ]
    assert len(body["flow"]["segments"]) == 6
    assert body["gap"]["script"]
    assert body["teams_notes"]
    assert "not leaked or official Schwab material" in body["disclaimer"]


def test_round1_questions_are_complete_and_unique(client):
    body = client.get("/api/round1").json()
    source_ids = {s["id"] for s in body["sources"]}
    ids = []
    for section in body["sections"]:
        for q in section["questions"]:
            ids.append(q["id"])
            assert q["prompt"].strip()
            assert q["why"].strip()
            assert q["model_answer"].strip()
            assert q["key_points"]
            assert q["follow_ups"]
            assert q["traps"]
            assert q["evidence"] in EVIDENCE
            assert q["source_ids"], q["id"]
            assert set(q["source_ids"]) <= source_ids, (q["id"], set(q["source_ids"]) - source_ids)
    assert len(ids) == len(set(ids)), "question ids must be unique"


def test_round1_flow_segments_have_rehearsal_answers(client):
    body = client.get("/api/round1").json()
    segments = body["flow"]["segments"]

    assert len(segments) == 6
    for segment in segments:
        assert segment["must_cover"], segment["minutes"]
        assert len(segment["must_cover"]) >= 3, segment["minutes"]
        # A usable rehearsal answer, not a one-liner.
        assert len(segment["example"]) >= 200, segment["minutes"]
        assert segment["example"].strip().startswith('"'), segment["minutes"]

    # The coding and API/SQL segments must also carry runnable snippets.
    with_code = [s for s in segments if s["example_code"].strip()]
    assert len(with_code) >= 2
    assert any("reverse" in s["example_code"] for s in with_code)
    assert any("SELECT" in s["example_code"] for s in with_code)


def test_round1_sources_are_labelled_and_linked(client):
    body = client.get("/api/round1").json()
    by_id = {s["id"]: s for s in body["sources"]}

    # Official evidence must be real schwabjobs.com pages.
    official = [s for s in body["sources"] if s["type"] == "official"]
    assert len(official) >= 4
    for source in official:
        assert source["url"].startswith("https://www.schwabjobs.com/"), source["id"]
        assert source["publisher"].startswith("Charles Schwab")
        assert source["supports"].strip()
        assert source["accessed"]

    # Every source type is known, and only the local brief may omit a URL.
    for source in body["sources"]:
        assert source["type"] in SOURCE_TYPES, source["id"]
        if source["type"] != "brief":
            assert source["url"].startswith("http"), source["id"]

    # The two claims the page leans on hardest are present.
    assert by_id["star"]["url"].endswith("/how-to-prepare-for-a-behavioral-based-interview")
    assert by_id["technology"]["url"].endswith("/technology")
    assert "Data Loss Prevention" in by_id["technology"]["supports"]
    assert "minimum of three" in by_id["star"]["supports"]


def test_round1_official_facts_cite_known_sources(client):
    body = client.get("/api/round1").json()
    source_ids = {s["id"] for s in body["sources"]}
    facts = body["official_process"]["facts"]
    assert len(facts) >= 5
    for fact in facts:
        assert fact["claim"].strip()
        assert fact["source_ids"]
        assert set(fact["source_ids"]) <= source_ids


def test_round1_count_appears_in_dashboard_inventory(client):
    content = client.get("/api/dashboard").json()["content"]
    assert content["round1_questions"] >= 20
