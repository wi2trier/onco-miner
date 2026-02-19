import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from fastapi.testclient import TestClient

import app as app_module
from helpers.config_loader import CONFIG


def _base_payload(sample_data: dict[str, dict[str, str]]) -> dict:
    return {
        "data": sample_data,
        "parameters": {
            "active_events": {
                "positive_events": [],
                "negative_events": [],
                "singular_events": [],
            },
            "n_top_variants": 2,
        },
    }


def test_health_endpoint_returns_status():
    client = TestClient(app_module.app)

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "Online"
    datetime.strptime(payload["timestamp"], "%Y-%m-%d %H:%M:%S")


def test_discover_returns_graph_and_metrics(sample_data):
    client = TestClient(app_module.app)

    response = client.post("/discover", json=_base_payload(sample_data))

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] is None
    assert payload["created"]

    connections = payload["graph"]["connections"]
    edge_frequencies = {(edge["e1"], edge["e2"]): edge["frequency"] for edge in connections}

    assert edge_frequencies[("start_node", "A")] == 2
    assert edge_frequencies[("A", "B")] == 1
    assert edge_frequencies[("A", "C")] == 1
    assert edge_frequencies[("B", "end_node")] == 1
    assert edge_frequencies[("C", "end_node")] == 1

    metrics = payload["metrics"]
    assert metrics["n_traces"] == 2
    assert metrics["n_events"] == 4
    assert metrics["n_variants"] == 2
    assert metrics["max_trace_length"] == 2
    assert metrics["min_trace_length"] == 2
    assert metrics["max_trace_duration"] == 172800.0
    assert metrics["min_trace_duration"] == 86400.0
    assert metrics["event_frequency_distr"] == {"A": 2, "B": 1, "C": 1}
    assert metrics["trace_length_distr"] == {"2": 2}

    if "tbe" in CONFIG["exclude"]:
        assert metrics["tbe"] is None
    if "active_events" in CONFIG["exclude"]:
        assert metrics["active_events"] is None


def test_discover_rejects_counts_and_states(sample_data):
    client = TestClient(app_module.app)

    payload = _base_payload(sample_data)
    payload["parameters"]["add_counts"] = True
    payload["parameters"]["state_changing_events"] = ["A"]

    response = client.post("/discover", json=payload)

    assert response.status_code == 400
    assert "states and counts" in response.json()["detail"].lower()


def test_discover_posts_callback(sample_data, monkeypatch):
    client = TestClient(app_module.app)
    calls: list[dict] = []

    def fake_post(url, json, timeout):
        calls.append({"url": url, "json": json, "timeout": timeout})
        return object()

    monkeypatch.setattr(app_module.requests, "post", fake_post)

    payload = _base_payload(sample_data)
    payload["callback_url"] = "https://example.com/callback"

    response = client.post("/discover", json=payload)

    assert response.status_code == 200
    assert len(calls) == 1
    assert calls[0]["url"] == "https://example.com/callback"
    assert calls[0]["timeout"] == app_module.REQUEST_TIMEOUT_SECONDS
    assert "graph" in calls[0]["json"]


def test_discover_with_sepsis_log():
    client = TestClient(app_module.app)

    data_path = Path(__file__).resolve().parents[1] / "test_logs" / "sepsis.json"
    with data_path.open() as file:
        sepsis_data = json.load(file)

    event_names = list(sepsis_data.get("concept:name", {}).values())
    top_events = [name for name, _ in Counter(event_names).most_common(3)]

    payload = {
        "data": sepsis_data,
        "parameters": {
            "active_events": {
                "positive_events": [],
                "negative_events": [],
                "singular_events": top_events,
            },
            "n_top_variants": 10,
            "reduce_complexity_by": 0,
            "add_counts": False,
            "state_changing_events": None,
        },
        "callback_url": None,
        "id": "test-sepsis",
    }

    response = client.post("/discover", json=payload)

    assert response.status_code == 200

    result = response.json()
    assert result["id"] == "test-sepsis"
    datetime.fromisoformat(result["created"])
    assert result["graph"]["connections"]

    metrics = result["metrics"]
    assert metrics["n_events"] == len(sepsis_data["concept:name"])
    assert metrics["n_traces"] == len(set(sepsis_data["case:concept:name"].values()))
    assert metrics["n_variants"] > 0

    if "top_variants" in CONFIG["exclude"]:
        assert metrics["top_variants"] is None
    else:
        assert 0 < len(metrics["top_variants"]) <= 10

    if "active_events" in CONFIG["exclude"]:
        assert metrics["active_events"] is None
    else:
        assert set(metrics["active_events"]) == {"yearly", "monthly", "weekly"}
