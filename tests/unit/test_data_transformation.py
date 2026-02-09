import pandas as pd

from data_transformation import add_counts, add_states, remove_counts, transform_dict


def test_transform_dict_converts_timestamp():
    data = {
        "concept:name": {"1": "A", "2": "B"},
        "case:concept:name": {"1": "T1", "2": "T1"},
        "time:timestamp": {"1": "2024-01-01T00:00:00", "2": "2024-01-02T00:00:00"},
    }

    df = transform_dict(data)

    assert list(df.columns) == ["concept:name", "case:concept:name", "time:timestamp"]
    assert pd.api.types.is_datetime64_any_dtype(df["time:timestamp"])
    assert df.loc["1", "time:timestamp"] == pd.Timestamp("2024-01-01T00:00:00")


def test_add_counts_numbers_events_per_trace():
    df = pd.DataFrame(
        {
            "case:concept:name": ["T1", "T1", "T1", "T2"],
            "concept:name": ["A", "B", "A", "B"],
            "time:timestamp": [
                "2024-01-01T00:00:00",
                "2024-01-02T00:00:00",
                "2024-01-03T00:00:00",
                "2024-01-01T00:00:00",
            ],
        }
    )

    counted = add_counts(df)

    assert list(counted["concept:name"]) == ["A_1", "B_1", "A_2", "B_1"]
    assert list(counted.columns) == ["case:concept:name", "concept:name", "time:timestamp"]


def test_add_states_adds_state_suffixes():
    df = pd.DataFrame(
        {
            "case:concept:name": ["T1", "T1", "T1", "T1"],
            "concept:name": ["Start", "X", "Start", "X"],
            "time:timestamp": [
                "2024-01-01T00:00:00",
                "2024-01-01T01:00:00",
                "2024-01-02T00:00:00",
                "2024-01-02T01:00:00",
            ],
        }
    )

    with_states = add_states(df, ["Start"])

    assert list(with_states["concept:name"]) == ["Start_1", "X_1", "Start_2", "X_2"]


def test_remove_counts_strips_suffix():
    df = pd.DataFrame(
        {
            "case:concept:name": ["T1", "T1"],
            "concept:name": ["A_1", "B_2"],
            "time:timestamp": ["2024-01-01T00:00:00", "2024-01-02T00:00:00"],
        }
    )

    cleaned = remove_counts(df)

    assert list(cleaned["concept:name"]) == ["A", "B"]
