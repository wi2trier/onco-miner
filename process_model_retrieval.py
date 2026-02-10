import numpy as np
import pandas as pd
import pm4py
from pm4py.objects.log.obj import EventLog

from response_model import Connection, Graph


def get_process_model(data: EventLog | pd.DataFrame, start_node_name: str, end_node_name: str) -> Graph:
    """
    Calculate directly follows graph with frequency of each graph edge
    as well as time statistics based on the given data.
    :param end_node_name: name of the node that represents the final node.
    :param start_node_name: name of the node that represents the first node.
    :param data: Data containing the traces.
    If dataframe, it should have the columns 'case:concept:name', 'concept:name' and 'time:timestamp'.
    :return: DFG with frequency and performance data.
    """
    data = data.copy()
    performance_pm = pm4py.discovery.discover_performance_dfg(data)
    frequency_pm = pm4py.discovery.discover_dfg(data)
    if performance_pm[1] != frequency_pm[1] or performance_pm[2] != frequency_pm[2]:
        raise Exception("Generated Graphs are not the same.")
    result_pm: Graph = Graph(connections=[])
    for key, val in frequency_pm[1].items():
        connection: Connection = Connection(e1=start_node_name, e2=key, frequency=val, median= -1, min= -1,
                                            max= -1, stdev= -1, sum= -1, mean= -1)
        result_pm.connections.append(connection)
    for el in performance_pm[0]:
        performance_values = performance_pm[0][el]
        if np.isnan(performance_values["stdev"]):
            performance_values["stdev"] = -1
        frequency_value = frequency_pm[0][el]
        connection = Connection(e1=el[0], e2=el[1], frequency=frequency_value,
                                            median=performance_values["median"], min=performance_values["min"],
                                            max=performance_values["max"], stdev=performance_values["stdev"],
                                            sum=performance_values["sum"], mean=performance_values["mean"])
        result_pm.connections.append(connection)
    for key, val in frequency_pm[2].items():
        connection = Connection(e1=key, e2=end_node_name, frequency=val, median= -1, min= -1,
                                            max= -1, stdev= -1, sum= -1, mean= -1)
        result_pm.connections.append(connection)
    return result_pm
