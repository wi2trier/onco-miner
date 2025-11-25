
import pandas as pd


def transform_dict(data: dict[str, dict[str, str]]) -> pd.DataFrame:
    loaded_data = pd.DataFrame.from_dict(data)
    loaded_data["time:timestamp"] = loaded_data["time:timestamp"].apply(lambda x: pd.to_datetime(x))
    return loaded_data
