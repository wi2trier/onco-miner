import time
from typing import cast

import matplotlib.pyplot as plt
import pm4py
import requests

from app import REQUEST_TIMEOUT_SECONDS, discover_process_model
import pandas as pd

from data_handling.data_validation import validate_data
from model.input_model import InputBody
from retrieval.metrics_retrieval import get_metrics
from retrieval.process_model_retrieval import get_process_model

url = "http://127.0.0.1:8000/discover"
percentages = [#0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,
               1]
amount = 100
base_data = "test_logs/sepsis.json"

base_request: dict[str, dict] = {
    "parameters": {},
    "data": {}
}

def run_test() -> tuple[list[list[float]], list[str]]:
    data = pd.read_json(base_data)
    data["time:timestamp"] = pd.to_datetime(data["time:timestamp"], format="ISO8601")
    results = []
    n_events = []
    for percentage in percentages:
        print("Starting test {}".format(percentage))
        df_reduced = data.iloc[:int(len(data) * percentage)]
        n_events.append(str(len(df_reduced)))
        request = base_request.copy()
        reduced_dict = cast(dict[str, dict[str, str]],df_reduced.to_dict())
        reduced_dict = {str(k): {str(k_1): str(v_1) for k_1, v_1 in v.items()} for k, v in reduced_dict.items()}
        request["data"] = reduced_dict
        request_input = InputBody.model_validate(request)
        timings = []
        for run in range(amount):
            print("Starting run {}".format(run))
            start = time.perf_counter()
            # Comment out whatever function you want to test
            #send_request(url, request)
            #get_process_model(df_reduced, "s", "e")
            get_metrics(df_reduced, None, 10)
            #validate_data(reduced_dict)
            #discover_process_model(request_input)
            end = time.perf_counter()
            timings.append(end - start)
            print("Finished run {} in {} seconds".format(run, end - start))
        result = {"min": min(timings),
                  "max": max(timings),
                  "mean": sum(timings) / len(timings)
                  }
        results.append(timings)
        print(result)
    return results, n_events




def send_request(url: str, data: dict) -> str:
    post_request = requests.post(
        url=url,
        json=data,

    )
    return post_request.text

if __name__ == "__main__":
    results, labels = run_test()

    fig, ax = plt.subplots()
    ax.set_ylabel('duration (seconds)')
    ax.set_xlabel('number of events')

    bplot = ax.boxplot(results,
                       tick_labels=labels)  # will be used to label x-ticks

    plt.show()


