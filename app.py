from fastapi import FastAPI
from process_model_retrieval import get_process_model as get_pm

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/process_model")
async def get_process_model(data):
    return {"message": get_pm(data)}
