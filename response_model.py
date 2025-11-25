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
    start_nodes: dict[str, int]
    end_nodes: dict[str, int]


class TimeBetweenEvents(BaseModel):
    e1: str
    e2: str
    time: str

class Metrics(BaseModel):
    n_cases: int
    n_events: int
    n_variants: int
    top_variants: dict[str, list[str]]
    tbe: list[TimeBetweenEvents]
    max_trace_length: int
    min_trace_length: int
    event_frequency_distr: dict[str, int]


class DiscoveryResponse(BaseModel):
    graph: Graph
    metrics: Metrics
    created: str
    id: str



