from data_handling.data_transformation import transform_dict
from helpers.config_loader import CONFIG
from model.input_model import ActiveEventParameters
from retrieval.metrics_retrieval import get_metrics


def _assert_metric(metrics, name: str, expected):
    if name in CONFIG["exclude"]:
        assert getattr(metrics, name) is None
    else:
        assert getattr(metrics, name) == expected


def test_get_metrics_small_dataset(sample_data):
    df = transform_dict(sample_data)
    active_events = ActiveEventParameters(
        positive_events=[],
        negative_events=[],
        singular_events=["A", "B", "C"],
    )

    metrics = get_metrics(df, active_events, n_top_variants=2)

    _assert_metric(metrics, "n_traces", 2)
    _assert_metric(metrics, "n_events", 4)
    _assert_metric(metrics, "n_variants", 2)
    _assert_metric(metrics, "max_trace_length", 2)
    _assert_metric(metrics, "min_trace_length", 2)
    _assert_metric(metrics, "max_trace_duration", 172800.0)
    _assert_metric(metrics, "min_trace_duration", 86400.0)
    _assert_metric(metrics, "event_frequency_distr", {"A": 2, "B": 1, "C": 1})
    _assert_metric(metrics, "trace_length_distr", {"2": 2})

    if "top_variants" in CONFIG["exclude"]:
        assert metrics.top_variants is None
    else:
        sequences = {tuple(variant.event_sequence) for variant in metrics.top_variants.values()}
        assert sequences == {("A", "B"), ("A", "C")}

    if "tbe" in CONFIG["exclude"]:
        assert metrics.tbe is None
    else:
        edges = {(edge.e1, edge.e2) for edge in metrics.tbe}
        assert edges == {("A", "B"), ("A", "C")}
        assert all(edge.frequency == -1 for edge in metrics.tbe)

    if "active_events" in CONFIG["exclude"]:
        assert metrics.active_events is None
    else:
        assert metrics.active_events.yearly
        assert all(isinstance(value, int) for value in metrics.active_events.yearly.values())
