import numpy as np
import pandas as pd
import pm4py
from pm4py.objects.log.obj import EventLog

from response_model import Connection, Graph


def get_process_model(input_data: EventLog|pd.DataFrame) -> Graph:
    data = input_data.copy()
    performance_pm = pm4py.discovery.discover_performance_dfg(data)
    frequency_pm = pm4py.discovery.discover_dfg(data)
    if performance_pm[1] != frequency_pm[1] or performance_pm[2] != frequency_pm[2]:
        raise Exception("Generated Graphs are not the same.")
    result_pm: Graph = Graph(connections=[], start_nodes=performance_pm[1], end_nodes=performance_pm[2])
    for el in performance_pm[0]:
        performance_values = performance_pm[0][el]
        if np.isnan(performance_values["stdev"]):
            performance_values["stdev"] = -1
        frequency_value = frequency_pm[0][el]
        connection: Connection = Connection(e1=el[0], e2=el[1], frequency=frequency_value,
                                            median=performance_values["median"], min=performance_values["min"],
                                            max=performance_values["max"], stdev=performance_values["stdev"],
                                            sum=performance_values["sum"], mean=performance_values["mean"])
        result_pm.connections.append(connection)
    return result_pm
