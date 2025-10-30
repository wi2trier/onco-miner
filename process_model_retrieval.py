import pm4py
from pm4py import BPMN
from pm4py.objects.log.obj import EventLog


def get_process_model(data: EventLog) -> BPMN:
    pm = pm4py.discover_bpmn_inductive(data)
    pm4py.view_bpmn(pm)
    return pm


