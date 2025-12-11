import json

import pandas as pd


def transform_dict(data: dict[str, dict[str, str]]) -> pd.DataFrame:
    """
    Turns dictionary of expected structure into a DataFrame and converts 'time:timestamp' string into a datetime object.
    :param data: Dictionary of expected structure.
    :return: DataFrame.
    """
    loaded_data = pd.DataFrame.from_dict(data)
    loaded_data["time:timestamp"] = pd.to_datetime(loaded_data["time:timestamp"], format = "ISO8601")
    return loaded_data

if __name__ == "__main__":
    with open('test_logs/sepsis.json') as f:
        json_data = json.load(f)
    transformed_data = transform_dict(json_data)
    print(list(transformed_data["concept:name"].value_counts().index))
