from data_handling.data_transformation import transform_dict
from retrieval.process_model_retrieval import get_process_model


def test_get_process_model_builds_expected_edges(sample_data):
    df = transform_dict(sample_data)

    graph = get_process_model(df, "START", "END")

    edge_frequencies = {(edge.e1, edge.e2): edge.frequency for edge in graph.connections}

    assert edge_frequencies[("START", "A")] == 2
    assert edge_frequencies[("A", "B")] == 1
    assert edge_frequencies[("A", "C")] == 1
    assert edge_frequencies[("B", "END")] == 1
    assert edge_frequencies[("C", "END")] == 1
    assert len(graph.connections) == 5
