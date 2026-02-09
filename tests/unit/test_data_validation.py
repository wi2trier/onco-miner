import pytest

from data_validation import validate_data


def _valid_data():
    return {
        "concept:name": {"1": "A", "2": "B"},
        "case:concept:name": {"1": "T1", "2": "T1"},
        "time:timestamp": {"1": "2024-01-01 00:00:00", "2": "2024-01-02 00:00:00"},
    }


def test_validate_data_accepts_valid_input():
    validate_data(_valid_data())


def test_validate_data_rejects_wrong_keys():
    data = _valid_data()
    data["wrong"] = data.pop("concept:name")

    with pytest.raises(ValueError):
        validate_data(data)


def test_validate_data_rejects_non_dict_values():
    data = _valid_data()
    data["concept:name"] = ["A", "B"]

    with pytest.raises(TypeError):
        validate_data(data)


def test_validate_data_rejects_mismatched_indices():
    data = _valid_data()
    data["case:concept:name"] = {"1": "T1"}  # different length

    with pytest.raises(ValueError):
        validate_data(data)


def test_validate_data_rejects_non_string_values():
    data = _valid_data()
    data["concept:name"]["2"] = 2

    with pytest.raises(TypeError):
        validate_data(data)


def test_validate_data_rejects_timezone():
    data = _valid_data()
    data["time:timestamp"]["2"] = "2024-01-02T00:00:00+01:00"

    with pytest.raises(ValueError):
        validate_data(data)


def test_validate_data_rejects_unsorted_events():
    data = _valid_data()
    data["time:timestamp"] = {
        "1": "2024-01-02 00:00:00",
        "2": "2024-01-01 00:00:00",
    }

    with pytest.raises(ValueError):
        validate_data(data)
