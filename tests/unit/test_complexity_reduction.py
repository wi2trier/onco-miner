import pandas as pd

from data_handling.complexity_reduction import reduce_dataframe


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "case:concept:name": [
                "T1", "T1",
                "T2", "T2",
                "T3", "T3",
                "T4", "T4",
                "T5", "T5",
                "T6", "T6",
                "T7", "T7",
            ],
            "concept:name": [
                "A", "B",   # T1
                "A", "B",   # T2
                "A", "B",   # T3
                "A", "B",   # T4
                "A", "C",   # T5
                "A", "C",   # T6
                "A", "D",   # T7
            ],
            "time:timestamp": [
                "2024-01-01T00:00:00", "2024-01-01T01:00:00",
                "2024-01-02T00:00:00", "2024-01-02T01:00:00",
                "2024-01-03T00:00:00", "2024-01-03T01:00:00",
                "2024-01-04T00:00:00", "2024-01-04T01:00:00",
                "2024-01-05T00:00:00", "2024-01-05T01:00:00",
                "2024-01-06T00:00:00", "2024-01-06T01:00:00",
                "2024-01-07T00:00:00", "2024-01-07T01:00:00",
            ],
        }
    )


def test_reduce_dataframe_keeps_most_frequent_variant():
    df = _sample_df()

    reduced = reduce_dataframe(df, percentage=0.5)

    assert set(reduced["case:concept:name"].unique()) == {"T1", "T2", "T3", "T4"}


def test_reduce_dataframe_percentage_0_2_keeps_top_variant_only():
    df = _sample_df()

    reduced = reduce_dataframe(df, percentage=0.2)

    assert set(reduced["case:concept:name"].unique()) == {"T1", "T2", "T3", "T4"}


def test_reduce_dataframe_percentage_0_8_keeps_top_two_variants():
    df = _sample_df()

    reduced = reduce_dataframe(df, percentage=0.8)

    assert set(reduced["case:concept:name"].unique()) == {"T1", "T2", "T3", "T4", "T5", "T6"}


def test_reduce_dataframe_percentage_one_keeps_all():
    df = _sample_df()

    reduced = reduce_dataframe(df, percentage=1.0)

    assert set(reduced["case:concept:name"].unique()) == {"T1", "T2", "T3", "T4", "T5", "T6", "T7"}
