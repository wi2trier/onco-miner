import json

import numpy as np
import pandas as pd


def transform_dict(data: dict[str, dict[str, str]]) -> pd.DataFrame:
    """
    Turns dictionary of expected structure into a DataFrame and converts 'time:timestamp' string into a datetime object.
    :param data: Dictionary of expected structure.
    :return: DataFrame.
    """
    loaded_data = pd.DataFrame.from_dict(data)
    loaded_data["time:timestamp"] = pd.to_datetime(loaded_data["time:timestamp"], format="ISO8601")
    return loaded_data


def add_counts(data: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a counter to each event in each trace.
    Each event type per trace gets its own counter.
    :param data: Data where the counter is to be added.
    :return: Data with added counter.
    """
    data = data.copy()
    data["counts"] = data.groupby(["case:concept:name", "concept:name"]).cumcount() + 1
    data["concept:name"] = data["concept:name"].astype(str) + "_" + data["counts"].astype(str)
    return data[["case:concept:name", "concept:name", "time:timestamp"]]


def add_states(data: pd.DataFrame, state_changing_events: list[str]) -> pd.DataFrame:
    """
    Adds states to each event in each trace.
    State changes are triggered by the state changing events.
    If there is more than one state changing event, the final events of the traces are combined,
    ignoring the state the trace is in.
    This leads to a less scattered graph.
    :param data: Data where states should be added.
    :param state_changing_events: Events that trigger a state change and are therefore state defining.
    :return: Data with added states.
    """
    data = data.copy()
    data["counts"] = data[data["concept:name"].isin(state_changing_events)].groupby(
        ["case:concept:name", "concept:name"]).cumcount() + 1
    state_frame = pd.get_dummies(data["concept:name"]).mul(data["counts"], axis=0).replace(0, np.nan)
    state_frame = state_frame.dropna(axis=1, how="all")
    first_rows = data.groupby('case:concept:name').cumcount().eq(0)
    state_frame.loc[first_rows] = state_frame.loc[first_rows].fillna(0)
    state_frame = state_frame.ffill()
    data["concept:name"] = data["concept:name"].astype(str) + "_" + state_frame.astype(str).to_numpy().sum(axis=1)
    data["concept:name"] = data["concept:name"].str[:-2]
    if len(state_changing_events) > 1:
        last_rows = data.groupby('case:concept:name').cumcount(ascending=False).eq(0)
        data.loc[last_rows] = remove_counts(data.loc[last_rows])
    return data[["case:concept:name", "concept:name", "time:timestamp"]]


def remove_counts(data: pd.DataFrame) -> pd.DataFrame:
    """
    Removes counts from each event in each trace.
    Works only on dataframes where states or counts where added.
    :param data: Data where counts are removed.
    :return: Data without counts.
    """
    data.loc[:, "concept:name"] = data.loc[:, "concept:name"].str.split("_").str[:-1].str.join("_")
    return data


if __name__ == "__main__":
    with open('test_logs/sepsis.json') as f:
        json_data = json.load(f)
    transformed_data = transform_dict(json_data)
    counted_data = remove_counts(add_counts(transformed_data))
    print(counted_data)
