import pm4py
from pm4py.objects.log.obj import EventLog


def get_process_model(data: EventLog) -> tuple[dict, dict, dict, dict]:
    performance_pm = pm4py.discovery.discover_performance_dfg(data)
    frequency_pm = pm4py.discovery.discover_dfg(data)
    result_pm = (performance_pm[0], frequency_pm[0], performance_pm[1], performance_pm[2])
    return result_pm


