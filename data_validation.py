from datetime import datetime

import pandas as pd

expected_features = ["concept:name", "case:concept:name", "time:timestamp"]


def datetime_valid(dt_str: str) -> bool:
    try:
        datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except ValueError:
        return False
    return True


def validate_data(data: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    """
    Checks if the data matches the expected format.
    :param data: Data to be validated.
    :return: Validated data (unchanged).
    """
    features = data.keys()
    if len(features) != 3:
        raise ValueError(f"Wrong number of keys. Expected 3, got {len(features)}.")
    for feature in features:
        if feature not in expected_features:
            raise ValueError(f"Wrong key. Expected {", ".join(expected_features)}, got {feature}.")
    concept_name_dict = data["concept:name"]
    case_concept_name_dict = data["case:concept:name"]
    time_timestamp_dict = data["time:timestamp"]
    for feature in expected_features:
        if not isinstance(data[feature], dict):
            raise TypeError(f"{data[feature]} has the wrong data type."
                            f" Expected dict, got {type(data[feature])}.")
    if not (len(concept_name_dict) == len(case_concept_name_dict) == len(time_timestamp_dict)):
        raise ValueError(f"Number of events, trace identifiers and timestamps do not match."
                         f" Got {len(concept_name_dict)} events,"
                         f" {len(case_concept_name_dict)} trace identifiers and {len(time_timestamp_dict)} timestamps.")
    for feature in expected_features:
        if len(set(data[feature])) != len(data[feature]):
            raise ValueError(f"Indices of {feature} are not unique.")
    if not (set(concept_name_dict.keys()) == set(case_concept_name_dict.keys()) == set(time_timestamp_dict.keys())):
        raise ValueError("Indices are not identical.")
    for value in concept_name_dict.values():
        if not isinstance(value, str):
            raise TypeError(f"{value} in concept:name has the wrong type. Expected str, got {type(value)}.")
    for value in case_concept_name_dict.values():
        if not isinstance(value, str):
            raise TypeError(f"{value} in case:concept:name has the wrong type. Expected str, got {type(value)}.")
    for value in time_timestamp_dict.values():
        if not isinstance(value, str):
            raise TypeError(f"{value} in time:timestamp has the wrong type. Expected str, got {type(value)}.")
        if not datetime_valid(value):
            raise ValueError(f"{value} is not valid ISO8601.")
    loaded_data = pd.DataFrame.from_dict(data)[["case:concept:name", "time:timestamp"]]
    loaded_data["time:timestamp"] = loaded_data["time:timestamp"].apply(lambda x: pd.to_datetime(x))
    grouped_data = loaded_data.groupby("case:concept:name").agg({"time:timestamp": list})
    grouped_data["sorted?"] = grouped_data["time:timestamp"].apply(lambda val: all(val[i] <= val[i + 1] for i in range(len(val) - 1)))
    if False in grouped_data["sorted?"]:
        raise ValueError("Events are not sorted.")
    return data
