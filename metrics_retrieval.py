import pandas as pd
from pm4py.statistics.variants.pandas.get import get_variants_count

from response_model import Metrics


def get_metrics(data: pd.DataFrame, n_top_variants: int=10) -> Metrics:
    variants = get_variants_count(data)
    top_variants = list(sorted(variants.items(), key=lambda item: item[1], reverse=True))[0:n_top_variants]
    top_variants_dict = {}
    for index, variant in enumerate(top_variants):
        top_variants_dict[str(index)] = list(variant[0])
    metrics = Metrics(n_cases=data["case:concept:name"].nunique(), n_events=len(data), n_variants=len(variants),
                      top_variants=top_variants_dict, tbe=[], max_trace_length=0, min_trace_length=0,
                      event_frequency_distr={})
    return metrics
