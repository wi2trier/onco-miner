
import pandas as pd
import pm4py


def transform_dict(data):
    loaded_data = pd.DataFrame.from_dict(data)
    loaded_data["time:timestamp"] = loaded_data["time:timestamp"].apply(lambda x: pd.to_datetime(x))
    event_log = pm4py.convert_to_event_log(loaded_data)
    return event_log
