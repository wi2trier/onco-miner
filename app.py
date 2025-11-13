from fastapi import FastAPI
from pydantic import BaseModel

from data_transformation import transform_dict
from process_model_retrieval import get_process_model
from stats_retrieval import get_process_stats


class DiscoverBody(BaseModel):
    data: dict
    output_type: str | None = None
    algorithm_name: str | None = None
    algorithm_params: dict | None = None
    callback_url: str | None = None


class DiscoveryResponse(BaseModel):
    result: tuple[dict, dict, dict, dict] | None
    error: dict | None


class StatsResponse(BaseModel):
    result: dict | None
    error: dict | None


class StatsBody(BaseModel):
    data: dict
    metrics: dict
    callback_url: str


app = FastAPI()


@app.post("/discover")
async def discover_process_model(request: DiscoverBody) -> DiscoveryResponse:
    result = None
    error = None
    event_log = transform_dict(request.data)
    try:
        result = get_process_model(event_log)
    except Exception as e:
        error = {
            "code": "",
            "message": "",
            "details": ""
        }
    return DiscoveryResponse(result=result, error=error)


@app.post("/stats")
async def collect_process_stats(request: StatsBody) -> StatsResponse:
    result = None
    error = None
    event_log = transform_dict(request.data)
    try:
        result = get_process_stats(event_log)
    except Exception as e:
        error = {
            "code": "",
            "message": "",
            "details": ""
        }
    return StatsResponse(result=result, error=error)


@app.get("/config/algorithms")
async def get_algorithms():
    algorithms = []
    return {"algorithms": algorithms}


@app.get("/health")
async def get_health():
    status = ""
    uptime = 0
    return {"status": status,
            "uptime_s": uptime}
