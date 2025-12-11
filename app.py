from datetime import datetime

import requests
import uvicorn
from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel

from data_transformation import transform_dict
from data_validation import validate_data
from input_model import InputBody
from metrics_retrieval import get_metrics
from process_model_retrieval import get_process_model
from response_model import DiscoveryResponse


class ResponseReceived(BaseModel):
    ok: bool


app = FastAPI(title="PROVIS cnco-miner API",
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


@process_model_callback_router.post("{$callback_url}", response_model=ResponseReceived)
def distribute_process_model(process_model: DiscoveryResponse) -> ResponseReceived:
    pass


@app.post("/discover", callbacks=process_model_callback_router.routes)
async def discover_process_model(request: InputBody) -> DiscoveryResponse:
    """
    API request to calculate a Process model and metrics based on the given data.
    :param request: Input data as well as necessary parameters and an id that will be returned with the result.
    :return: Calculated Process Model, metrics, creation time and id provided in the request.
    """
    try:
        validate_data(request.data)
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    event_log = transform_dict(request.data)
    graph = get_process_model(event_log)
    if request.parameters.n_top_variants:
        metrics = get_metrics(event_log, request.parameters.active_events, request.parameters.n_top_variants)
    else:
        metrics = get_metrics(event_log, request.parameters.active_events)
    creation_time = str(datetime.now())
    response = DiscoveryResponse(graph=graph, metrics=metrics, created=creation_time, id="None")
    if request.callback_url is not None:
        try:
            requests.post(url=str(request.callback_url), json=response.model_dump(mode="python"))
        except requests.exceptions.ConnectionError as e:
            raise HTTPException(status_code=500, detail=str(e)) from e
    return response


@app.get("/config/algorithms")
async def get_algorithms() -> dict[str, list[str]]:
    algorithms: list[str] = []
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
