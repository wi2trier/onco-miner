from pydantic import BaseModel


class Connection(BaseModel):
    e1: str
    e2: str
    frequency: int
    median: float
    min: float
    max: float
    stdev: float
    sum: float
    mean: float

class Graph(BaseModel):
    connections: list[Connection]


class TimeBetweenEvents(BaseModel):
    e1: str
    e2: str
    time: str


class ActiveEvents(BaseModel):
    yearly: dict[str, int]
    monthly: dict[str, int]
    weekly: dict[str, int]

class Metrics(BaseModel):
    n_cases: int
    n_events: int
    n_variants: int
    top_variants: dict[str, list[str]]
    tbe: list[Connection]
    max_trace_length: int
    min_trace_length: int
    max_trace_duration: float
    min_trace_duration: float
    active_events: ActiveEvents
    event_frequency_distr: dict[str, int]
    trace_length_distr: dict[str, int]


class DiscoveryResponse(BaseModel):
    graph: Graph
    metrics: Metrics
    created: str
    id: str



