import numpy as np
import pandas as pd
import pm4py
import pytest


@pytest.fixture()
def sample_data() -> dict[str, dict[str, str]]:
    return {
        "concept:name": {"1": "A", "2": "B", "3": "A", "4": "C"},
        "case:concept:name": {"1": "T1", "2": "T1", "3": "T2", "4": "T2"},
        "time:timestamp": {
            "1": "2024-01-01T00:00:00",
            "2": "2024-01-02T00:00:00",
            "3": "2024-01-01T00:00:00",
            "4": "2024-01-03T00:00:00",
        },
    }


@pytest.fixture(autouse=True)
def _pm4py_performance_seconds(monkeypatch):
    original = pm4py.discovery.discover_performance_dfg

    def to_seconds(value):
        if value is None or pd.isna(value):
            return float("nan")
        if isinstance(value, (int, float, np.floating)):
            return float(value)
        if isinstance(value, pd.Timedelta):
            return float(value.total_seconds())
        if isinstance(value, np.timedelta64):
            return float(value / np.timedelta64(1, "s"))
        if hasattr(value, "total_seconds"):
            try:
                return float(value.total_seconds())
            except (TypeError, ValueError):
                return float("nan")
        try:
            return float(value)
        except (TypeError, ValueError):
            return float("nan")

    def wrapped(*args, **kwargs):
        performance_dfg, start_activities, end_activities = original(*args, **kwargs)
        converted = {}
        for edge, stats in performance_dfg.items():
            converted_stats = {}
            for key, value in stats.items():
                converted_stats[key] = to_seconds(value)
            converted[edge] = converted_stats
        return converted, start_activities, end_activities

    monkeypatch.setattr(pm4py.discovery, "discover_performance_dfg", wrapped)
