import time
import matplotlib.pyplot as plt
import requests

from app import REQUEST_TIMEOUT_SECONDS
import pandas as pd

url = "http://127.0.0.1:8000/discover"
percentages = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]
amount = 10
base_data = "test_logs/sepsis.json"

base_request = {
    "parameters": {},
    "data": {}
}

def run_test():
    data = pd.read_json(base_data)
    results = []
    n_events = []
    print(send_request(url, base_request))
    for percentage in percentages:
        print("Starting test {}".format(percentage))
        df_reduced = data.iloc[:int(len(data) * percentage)]
        n_events.append(str(len(df_reduced)))
        request = base_request.copy()
        request["data"] = df_reduced.to_dict()
        timings = []
        for run in range(amount):
            print("Starting run {}".format(run))
            start = time.perf_counter()
            send_request(url, request)
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
        timeout=REQUEST_TIMEOUT_SECONDS,
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


