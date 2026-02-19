import pytest
from pydantic import ValidationError

from model.input_model import InputBody


def test_input_body_defaults(sample_data):
    body = InputBody.model_validate({"data": sample_data, "parameters": {}})

    assert body.parameters.n_top_variants == 10
    assert body.parameters.add_counts is False
    assert body.parameters.reduce_complexity_by == 0
    assert body.parameters.state_changing_events is None
    assert body.parameters.active_events is None
    assert body.parameters.start_node_name == "start_node"
    assert body.parameters.end_node_name == "end_node"
    assert body.callback_url is None
    assert body.id is None


def test_input_body_accepts_callback_url(sample_data):
    body = InputBody.model_validate(
        {"data": sample_data, "parameters": {}, "callback_url": "https://example.com/callback"}
    )

    assert str(body.callback_url) == "https://example.com/callback"


def test_input_body_requires_parameters(sample_data):
    with pytest.raises(ValidationError):
        InputBody.model_validate({"data": sample_data})
