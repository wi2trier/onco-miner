import os
from datetime import datetime

import requests
import uvicorn
from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel

from data_handling.complexity_reduction import reduce_dataframe
from data_handling.data_transformation import add_counts, add_states, transform_dict
from data_handling.data_validation import validate_data
from helpers import config_loader
from model.input_model import InputBody
from model.response_model import DiscoveryResponse
from retrieval.metrics_retrieval import get_metrics
from retrieval.process_model_retrieval import get_process_model


class ResponseReceived(BaseModel):
    ok: bool


app = FastAPI(title="PROVIS onco-miner API",
              description="This API is part of a project"
                          " to provide an process model based view on cancer patient data.",
              version="1.0.0",
              contact={
                  "name": "Eric Brake",
                  "email": "eric.brake@dfki.de",
              },
              license_info={
                  "name": "GNU GPL-3",
                  "url": "https://fsf.org/",
              })

process_model_callback_router = APIRouter()

REQUEST_TIMEOUT_SECONDS = 60


@process_model_callback_router.post("{$callback_url}", response_model=ResponseReceived)
def distribute_process_model(process_model: DiscoveryResponse) -> ResponseReceived:
    return ResponseReceived(ok=True)


@app.post("/discover", callbacks=process_model_callback_router.routes)
def discover_process_model(request: InputBody) -> DiscoveryResponse:
    """
    API request to calculate a Process model and metrics based on the given data.
    :param request: Input data as well as necessary parameters and an id that will be returned with the result.
    :return: Calculated Process Model, metrics, creation time and id provided in the request.
    """
    params = request.parameters
    try:
        validate_data(request.data)
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    if params.add_counts and params.state_changing_events:
        raise HTTPException(status_code=400, detail="Can not have states and counts at the same time.")
    pm_event_log = transform_dict(request.data)
    if params.reduce_complexity_by:
        pm_event_log = reduce_dataframe(pm_event_log, 1 - params.reduce_complexity_by)
    if params.add_counts:
        pm_event_log = add_counts(pm_event_log)
    elif params.state_changing_events:
        pm_event_log = add_states(pm_event_log, params.state_changing_events)
    graph = get_process_model(pm_event_log, params.start_node_name, params.end_node_name)
    metrics = get_metrics(pm_event_log, params.active_events, params.n_top_variants)
    creation_time = str(datetime.now())
    response = DiscoveryResponse(graph=graph, metrics=metrics, created=creation_time,
                                 id=None if request.id is None else str(request.id))
    if request.callback_url is not None:
        try:
            requests.post(
                url=str(request.callback_url),
                json=response.model_dump(mode="python"),
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=str(e)) from e
    return response


class HealthResponse(BaseModel):
    status: str
    timestamp: str


@app.get("/health")
async def get_health() -> HealthResponse:
    status = "Online"
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return HealthResponse(status=status, timestamp=ts)


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    print(config_loader.CONFIG)
    uvicorn.run(app, host=host, port=port)
