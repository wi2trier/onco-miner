from pydantic import BaseModel
from pydantic_core import Url


class ActiveEventParameters(BaseModel):
    positive_events: list[str]
    negative_events: list[str]
    singular_events: list[str]

class InputParameters(BaseModel):
    active_events: ActiveEventParameters
    n_top_variants: int | None = 10
    reduce_complexity_by: float | None = 0
    add_counts: bool | None = False
    state_changing_events: list[str] | None = None
    start_node_name: str = "start_node"
    end_node_name: str = "end_node"

class InputBody(BaseModel):
    data: dict[str, dict[str, str]]
    parameters: InputParameters
    callback_url: Url | None = None
    id: str | None = None
