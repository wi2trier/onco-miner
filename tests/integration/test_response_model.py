import json

from model.response_model import ActiveEvents, Connection, DiscoveryResponse, Graph, Metrics, TopVariant


def _sample_response() -> DiscoveryResponse:
    graph = Graph(
        connections=[
            Connection(
                e1="A",
                e2="B",
                frequency=2,
                median=1.5,
                min=1.0,
                max=2.0,
                stdev=0.5,
                sum=3.0,
                mean=1.5,
            )
        ]
    )
    metrics = Metrics(
        n_traces=2,
        n_events=4,
        n_variants=2,
        top_variants={"0": TopVariant(event_sequence=["A,B"], frequency=1, mean_duration=1),
                      "1": TopVariant(event_sequence=["A", "C"],
                                      frequency=2,
                                      mean_duration=1.5)},
        tbe=[
            Connection(
                e1="A",
                e2="B",
                frequency=-1,
                median=1.0,
                min=1.0,
                max=1.0,
                stdev=0.0,
                sum=1.0,
                mean=1.0,
            )
        ],
        max_trace_length=2,
        min_trace_length=2,
        max_trace_duration=86400.0,
        min_trace_duration=86400.0,
        active_events=ActiveEvents(
            yearly={"2024-01-01": 2},
            monthly={"2024-01-01": 2},
            weekly={"2024-01-01": 2},
        ),
        event_frequency_distr={"A": 2, "B": 1, "C": 1},
        trace_length_distr={"2": 2},
    )
    return DiscoveryResponse(
        graph=graph,
        metrics=metrics,
        created="2024-01-04 00:00:00",
        id="case-1",
    )


def test_discovery_response_roundtrip_with_models():
    response = _sample_response()

    dumped = response.model_dump(mode="python")
    json.dumps(dumped)

    roundtrip = DiscoveryResponse.model_validate(dumped)

    assert roundtrip.metrics.n_traces == 2
    assert roundtrip.metrics.n_events == 4
    assert roundtrip.graph.connections
    assert roundtrip.graph.connections[0].e1 == "A"


def test_discovery_response_accepts_dict_payload():
    payload = {
        "graph": {
            "connections": [
                {
                    "e1": "A",
                    "e2": "B",
                    "frequency": 1,
                    "median": 1.0,
                    "min": 1.0,
                    "max": 1.0,
                    "stdev": 0.0,
                    "sum": 1.0,
                    "mean": 1.0,
                }
            ],
            "start_nodes": {"A": 1},
            "end_nodes": {"B": 1},
        },
        "metrics": {
            "n_traces": 1,
            "n_events": 2,
            "n_variants": 1,
            "top_variants": {
                "0": {
                    "event_sequence": ["A", "B"],
                    "frequency": 1,
                    "mean_duration": 1.0
                }
            },
            "tbe": [
                {
                    "e1": "A",
                    "e2": "B",
                    "frequency": -1,
                    "median": 1.0,
                    "min": 1.0,
                    "max": 1.0,
                    "stdev": 0.0,
                    "sum": 1.0,
                    "mean": 1.0,
                }
            ],
            "max_trace_length": 2,
            "min_trace_length": 2,
            "max_trace_duration": 3600.0,
            "min_trace_duration": 3600.0,
            "active_events": {
                "yearly": {"2024-01-01": 1},
                "monthly": {"2024-01-01": 1},
                "weekly": {"2024-01-01": 1},
            },
            "event_frequency_distr": {"A": 1, "B": 1},
            "trace_length_distr": {"2": 1},
        },
        "created": "2024-01-01 00:00:00",
        "id": "payload-1",
    }

    response = DiscoveryResponse.model_validate(payload)

    assert response.metrics.active_events.weekly["2024-01-01"] == 1
    assert response.metrics.tbe[0].e1 == "A"
