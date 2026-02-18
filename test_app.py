import json

from data_handling.data_transformation import transform_dict
from data_handling.data_validation import validate_data
from model.input_model import ActiveEventParameters, InputBody, InputParameters
from retrieval.process_model_retrieval import get_process_model as get_pm


def get_process_model(data):
    validate_data(data)
    transformed_data = transform_dict(data)
    return {"message": get_pm(transformed_data)}


if __name__ == "__main__":
    with open('test_logs/sepsis.json') as f:
        json_data = json.load(f)
    pm = get_process_model(json_data)
    print(get_process_model(json_data))
    body = InputBody(data=json_data, parameters=InputParameters(active_events=ActiveEventParameters(positive_events=[],
                                                                                                    negative_events=[],
                                                                                                    singular_events=[])))
