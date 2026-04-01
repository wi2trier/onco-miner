import pandas as pd
from pm4py.statistics.variants.pandas.get import get_variants_count


def reduce_dataframe(data: pd.DataFrame, percentage: float) -> pd.DataFrame:
    """
    Removes traces from dataframe until a dataframe with the length
    of the given percentage of the original dataframe is reached.
    Removes the traces based on the occurrence rate of their variant (the order of the events occurring in the trace).
    Often occurring variants are kept.
    :param data: Dataframe that should be reduced.
    :param percentage: Percentage of the dataframe that should be kept.
    :return: Reduced dataframe.
    """
    n_traces = data.nunique()["case:concept:name"]
    variants: dict[list[str], int] = get_variants_count(data)
    top_variants: list[tuple[list[str], int]] = list(sorted(variants.items(), key=lambda item: item[1], reverse=True))
    needed_variants: list[list[str]] = []
    counter = 0
    necessary_traces = percentage * n_traces
    for variant in top_variants:
        if counter > necessary_traces:
            break
        needed_variants.append(variant[0])
        counter += variant[1]
    needed_variants = [list(x) for x in needed_variants]
    grouped_data = data.groupby("case:concept:name", as_index=False).agg({"concept:name": list})
    relevant_traces = grouped_data[grouped_data["concept:name"].isin(needed_variants)]["case:concept:name"]
    relevant_data = data[data["case:concept:name"].isin(relevant_traces)]
    return relevant_data

