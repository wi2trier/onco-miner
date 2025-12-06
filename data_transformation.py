
import pandas as pd


def transform_dict(data: dict[str, dict[str, str]]) -> pd.DataFrame:
    """
    Turns dictionary of expected structure into a DataFrame and converts 'time:timestamp' string into a datetime object.
    :param data: Dictionary of expected structure.
    :return: DataFrame.
    """
    loaded_data = pd.DataFrame.from_dict(data)
    loaded_data["time:timestamp"] = loaded_data["time:timestamp"].apply(lambda x: pd.to_datetime(x))
    return loaded_data
