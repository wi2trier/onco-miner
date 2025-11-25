from datetime import datetime

import uvicorn
from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel
from pydantic_core import Url

from data_transformation import transform_dict
from data_validation import validate_data
from metrics_retrieval import get_metrics
from process_model_retrieval import get_process_model
from response_model import DiscoveryResponse


class DiscoveryBody(BaseModel):
    data: dict[str, dict[str, str]]
    output_type: str | None = None
    algorithm_name: str | None = None
    algorithm_params: dict[str, str] | None = None
    callback_url: Url | None = None


class ResponseReceived(BaseModel):
    ok: bool


app = FastAPI()
process_model_callback_router = APIRouter()


@process_model_callback_router.post("{$callback_url}", response_model=ResponseReceived)
def distribute_process_model(process_model: DiscoveryResponse) -> ResponseReceived:
    pass


@app.post("/discover", callbacks=process_model_callback_router.routes)
async def discover_process_model(request: DiscoveryBody) -> DiscoveryResponse:
    try:
        validate_data(request.data)
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    event_log = transform_dict(request.data)
    graph = get_process_model(event_log)
    metrics = get_metrics(event_log)
    creation_time = str(datetime.now())
    response = DiscoveryResponse(graph=graph, metrics=metrics, created=creation_time, id="None")
    if request.callback_url is not None:
        print(str(request.callback_url))
        #requests.post(url=str(request.callback_url), json=response.model_dump_json())
    return response


@app.get("/config/algorithms")
async def get_algorithms() -> dict[str, list[str]]:
    algorithms: list[str]= []
    return {"algorithms": algorithms}


class HealthResponse(BaseModel):
    status: str
    uptime_s: int
@app.get("/health")
async def get_health() -> HealthResponse:
    status = ""
    uptime = 0
    return HealthResponse(status=status, uptime_s=uptime)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
