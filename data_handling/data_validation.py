from datetime import datetime

import pandas as pd

from data_handling.data_transformation import transform_dict

expected_features = ["concept:name", "case:concept:name", "time:timestamp"]


def _datetime_valid(dt_str: str) -> bool:
    """
    Checks if a string meets the ISO 8601 datetime format.
    :param dt_str: String to check.
    :return: true if the string meets the ISO 8601 datetime format, else false.
    """
    try:
        datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except ValueError:
        return False
    return True

def _datetime_no_timezone(dt_str: str) -> bool:
    return len(dt_str.split("+")) == 1


def _validate_column_names(data: dict[str, dict[str, str]]) -> None:
    """
    Validates that the keys in the outer dictionary are correct.
    These later define the column names of the data frame.
    :param data: Dictionary of data to validate.
    :return:
    """
    features = data.keys()
    if len(features) != 3:
        raise ValueError(f"Wrong number of keys. Expected 3, got {len(features)}.")
    for feature in features:
        if feature not in expected_features:
            raise ValueError(
                f"Wrong key. Expected {', '.join(expected_features)}, got {feature}."
            )


def _validate_column_types(data: dict[str, dict[str, str]]) -> None:
    """
    Validates that the values of the outer dictionary are dicts.
    :param data: Dictionary of data to validate.
    :return:
    """
    for feature in expected_features:
        if not isinstance(data[feature], dict):
            raise TypeError(f"{data[feature]} has the wrong data type."
                            f" Expected dict, got {type(data[feature])}.")


def _validate_indices(data: dict[str, dict[str, str]], concept_name_dict: dict[str, str],
                      case_concept_name_dict: dict[str, str], time_timestamp_dict: dict[str, str]) -> None:
    """
    Validates that the keys of the inner dictionaries are consistent throughout the inner dictionaries.
    These keys make the row indices in the data frame.
    :param data: Dictionary of data to validate.
    :param concept_name_dict: Inner dictionary containing concept:names.
    :param case_concept_name_dict: Inner dictionary containing case:concept:names.
    :param time_timestamp_dict: Inner dictionary containing time:timestamps.
    :return:
    """
    if not (len(concept_name_dict) == len(case_concept_name_dict) == len(time_timestamp_dict)):
        raise ValueError(f"Number of events, trace identifiers and timestamps do not match."
                         f" Got {len(concept_name_dict)} events,"
                         f" {len(case_concept_name_dict)} trace identifiers and {len(time_timestamp_dict)} timestamps.")
    for feature in expected_features:
        if len(set(data[feature])) != len(data[feature]):
            raise ValueError(f"Indices of {feature} are not unique.")
    if not (set(concept_name_dict.keys()) == set(case_concept_name_dict.keys()) == set(time_timestamp_dict.keys())):
        raise ValueError("Indices are not identical.")


def _validate_value_types(concept_name_dict: dict[str, str], case_concept_name_dict: dict[str, str],
                          time_timestamp_dict: dict[str, str]) -> None:
    """
    Validates that the values of the inner dictionaries have the right types (strings).
    Specifically checks if each time:timestamp values is ISO 8601 conformant.
    :param concept_name_dict: Inner dictionary containing concept:names.
    :param case_concept_name_dict: Inner dictionary containing case:concept:names.
    :param time_timestamp_dict: Inner dictionary containing time:timestamps.
    :return:
    """
    for value in concept_name_dict.values():
        if not isinstance(value, str):
            raise TypeError(f"{value} in concept:name has the wrong type. Expected str, got {type(value)}.")
    for value in case_concept_name_dict.values():
        if not isinstance(value, str):
            raise TypeError(f"{value} in case:concept:name has the wrong type. Expected str, got {type(value)}.")
    for value in time_timestamp_dict.values():
        if not isinstance(value, str):
            raise TypeError(f"{value} in time:timestamp has the wrong type. Expected str, got {type(value)}.")
        if not _datetime_valid(value):
            raise ValueError(f"{value} is not valid ISO8601.")
        if not _datetime_no_timezone(value):
            raise ValueError(f"{value} should not contain a time zone.")


def _validate_sorting(data: dict[str, dict[str, str]]) -> None:
    """
    Validates that the rows of the data frame built from the given data is sorted within each trace
    (defined by case:concept:names).
    :param data: Dictionary of data to validate.
    :return:
    """
    loaded_data = transform_dict(data)[["case:concept:name", "time:timestamp"]]
    if not (
            loaded_data
                    .groupby("case:concept:name")["time:timestamp"]
                    .diff()
                    .dropna()
                    .ge(pd.Timedelta(0))
                    .all()
    ):
        raise ValueError("Events are not sorted.")


def validate_data(data: dict[str, dict[str, str]]) -> None:
    """
    Checks if the data matches the expected format.
    :param data: Data to be validated.
    :return:
    """
    _validate_column_names(data)
    _validate_column_types(data)
    concept_name_dict = data["concept:name"]
    case_concept_name_dict = data["case:concept:name"]
    time_timestamp_dict = data["time:timestamp"]
    _validate_indices(data, concept_name_dict, case_concept_name_dict, time_timestamp_dict)
    _validate_value_types(concept_name_dict, case_concept_name_dict, time_timestamp_dict)
    _validate_sorting(data)
