import json

from data_transformation import transform_dict
from data_validation import validate_data
from process_model_retrieval import get_process_model as get_pm


def get_process_model(data):
    validated_data = validate_data(data)
    transformed_data = transform_dict(validated_data)
    return {"message": get_pm(transformed_data)}


if __name__ == "__main__":
    with open("test_logs/sepsis.json") as f:
        json_data = json.load(f)
    pm = get_process_model(json_data)
    print(get_process_model(json_data))
