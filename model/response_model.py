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


class TopVariant(BaseModel):
    event_sequence: list[str]
    frequency: int
    mean_duration: float


class Metrics(BaseModel):
    n_traces: int | None = None
    n_events: int | None = None
    n_variants: int | None = None
    top_variants: dict[str, TopVariant] | None = None
    tbe: list[Connection] | None = None
    max_trace_length: int | None = None
    min_trace_length: int | None = None
    max_trace_duration: float | None = None
    min_trace_duration: float | None = None
    active_events: ActiveEvents | None = None
    event_frequency_distr: dict[str, int] | None = None
    trace_length_distr: dict[str, int] | None = None


class DiscoveryResponse(BaseModel):
    graph: Graph
    metrics: Metrics
    created: str
    id: str | None
