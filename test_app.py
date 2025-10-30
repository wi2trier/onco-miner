import json
import ast

from data_transformation import transform_dict
from data_validation import validate_data
from process_model_retrieval import get_process_model as get_pm

def get_process_model(data):
    transformed_data = transform_dict(data)
    validated_data = validate_data(transformed_data)
    return {"message": get_pm(validated_data)}


if __name__ == "__main__":
    with open('test_logs/sepsis.json', 'r') as f:
        json_data = ast.literal_eval(json.load(f))

    print(get_process_model(json_data))