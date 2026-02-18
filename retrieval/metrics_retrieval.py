from dataclasses import dataclass

import numpy as np
import pandas as pd
import pm4py
from dateutil.relativedelta import relativedelta
from pandas.core.groupby import DataFrameGroupBy
from pm4py.statistics.variants.pandas.get import get_variants_count

from helpers.config_loader import CONFIG
from model.input_model import ActiveEventParameters
from model.response_model import ActiveEvents, Connection, Metrics, TopVariant


@dataclass
class Context:
    data: pd.DataFrame
    grouped_data: DataFrameGroupBy
    variants: dict[list[str], int]
    top_variants: list[tuple[list[str], int]]
    active_event_parameters: ActiveEventParameters | None


def get_time_between_events(context: Context) -> list[Connection]:
    """
    calculates statistics regarding the time between events of the top variants.
    :param context: contains precalculated data.
    :return: list of edges with statistics between events of the top variants.
    """
    top_variants = context.top_variants
    agg_data = context.grouped_data.agg({"concept:name": list, "time:timestamp": list})
    data: pd.DataFrame = context.data
    top_variants_list = [list(x[0]) for x in top_variants]
    relevant_traces = agg_data[agg_data["concept:name"].isin(top_variants_list)]["case:concept:name"]
    relevant_data = data[data["case:concept:name"].isin(relevant_traces)]
    performance_dfg = pm4py.discovery.discover_performance_dfg(relevant_data)
    result_list = []
    for el in performance_dfg[0]:
        performance_values = performance_dfg[0][el]
        if np.isnan(performance_values["stdev"]):
            performance_values["stdev"] = -1
        connection: Connection = Connection(e1=el[0], e2=el[1], frequency=-1,
                                            median=performance_values["median"], min=performance_values["min"],
                                            max=performance_values["max"], stdev=performance_values["stdev"],
                                            sum=performance_values["sum"], mean=performance_values["mean"])
        result_list.append(connection)
    return result_list


def get_max_trace_length(context: Context) -> int:
    return int(context.data["case:concept:name"].value_counts().max())


def get_min_trace_length(context: Context) -> int:
    return int(context.data["case:concept:name"].value_counts().min())


def get_min_trace_duration(context: Context) -> float:
    min_values = context.grouped_data.min()["time:timestamp"]
    max_values = context.grouped_data.max()["time:timestamp"]
    difference = max_values - min_values
    min_diff: pd.Timedelta = difference.min()
    return float(min_diff.total_seconds())


def get_max_trace_duration(context: Context) -> float:
    min_values = context.grouped_data.min()["time:timestamp"]
    max_values = context.grouped_data.max()["time:timestamp"]
    difference = max_values - min_values
    max_diff: pd.Timedelta = difference.max()
    return float(max_diff.total_seconds())


def get_event_frequency_distribution(context: Context) -> dict[str, int]:
    """
    Calculates the frequency of each event in the data.
    :param context: contains precalculated data.
    :return: Dictionary with event as key and frequency as value.
    """
    distr: dict[str, int] = context.data["concept:name"].value_counts().to_dict()
    return distr


def get_trace_length_distribution(context: Context) -> dict[str, int]:
    """
    Calculates how often each trace length occurred.
    :param context: contains precalculated data.
    :return: Dictionary with length as key and frequency as value.
    """
    distr: dict[str, int] = context.data["case:concept:name"].value_counts().to_dict()
    return distr


def calculate_weekly_bins(initial_timestamp: pd.Timestamp, final_timestamp: pd.Timestamp) -> list[pd.Timestamp]:
    """
    Calculates the start timestamp (Monday 00:00) for each week occurring in the time frame between the two timestamps.
    The initial timestamp is included in the first week and final timestamp is included in the last week.
    :param initial_timestamp: first timestamp.
    :param final_timestamp: last timestamp.
    :return: List of timestamps.
    """
    start_of_week: pd.Timestamp = initial_timestamp - pd.Timedelta(days=initial_timestamp.weekday())
    start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    week_starts = [start_of_week]
    while start_of_week <= final_timestamp:
        week_starts.append(start_of_week)
        start_of_week = start_of_week + pd.Timedelta(days=7)
    return week_starts


def calculate_monthly_bins(initial_timestamp: pd.Timestamp, final_timestamp: pd.Timestamp) -> list[pd.Timestamp]:
    """
    Calculates the start timestamp (1st of month, 00:00)
    for each month occurring in the time frame between the two timestamps.
    The initial timestamp is included in the first month and final timestamp is included in the last month.
    :param initial_timestamp: first timestamp.
    :param final_timestamp: last timestamp.
    :return: List of timestamps.
    """
    start_of_month = initial_timestamp - pd.Timedelta(days=initial_timestamp.day - 1)
    start_of_month.replace(hour=0, minute=0, second=0, microsecond=0)
    month_starts = [start_of_month]
    while start_of_month <= final_timestamp:
        month_starts.append(start_of_month)
        start_of_month = start_of_month + relativedelta(months=1)
    return month_starts


def calculate_yearly_bins(initial_timestamp: pd.Timestamp, final_timestamp: pd.Timestamp) -> list[pd.Timestamp]:
    """
    Calculates the start timestamp (January 1st, 00:00)
    for each week occurring in the time frame between the two timestamps.
    The initial timestamp is included in the first year and final timestamp is included in the last year.
    :param initial_timestamp: first timestamp.
    :param final_timestamp: last timestamp.
    :return: List of timestamps.
    """
    start_of_year = pd.Timestamp(year=initial_timestamp.year, month=1, day=1)
    year_starts = []
    while start_of_year <= final_timestamp:
        year_starts.append(start_of_year)
        start_of_year = start_of_year + relativedelta(years=1)
    return year_starts


def calculate_bin_values(data: pd.DataFrame, bin_starts: list[pd.Timestamp],
                         active_event_parameters: ActiveEventParameters) -> dict[str, int]:
    """
    Calculates the amount of active events for each timeframe between two consecutive timestamps.
    :param active_event_parameters: Parameters to calculate the active events per timeframe.
    Consists of positive events, which mark the start of a specific timeframe bordered by two events,
    of negative events, which mark the end of such a timeframe, and singular events.
    :param data: Data from which the active events are calculated.
    :param bin_starts: timestamps used as bin starts.
    :return: Dictionary with timestamp as key and number of active events as value.
    """
    positive_events: list[str] = active_event_parameters.positive_events
    negative_events: list[str] = active_event_parameters.negative_events
    singular_events: list[str] = active_event_parameters.singular_events
    bin_dict = {}
    n_bins = len(bin_starts)
    active_events = 0
    for i, bin_start in enumerate(bin_starts):
        bin_end = bin_starts[i + 1] if i < n_bins - 1 else pd.Timestamp.now()
        pre_bin_start = bin_starts[i - 1] if i > 0 else bin_start - pd.Timedelta(days=1)
        bin_data = data[data["time:timestamp"].between(bin_start, bin_end, inclusive="left")]
        pre_bin_data = data[data["time:timestamp"].between(pre_bin_start, bin_start, inclusive="left")]
        active_events += len(bin_data[bin_data["concept:name"].isin(positive_events)]) - len(
            pre_bin_data[pre_bin_data["concept:name"].isin(negative_events)])
        amount = active_events + len(bin_data[bin_data["concept:name"].isin(singular_events)])
        bin_dict[str(bin_start)] = amount
    return bin_dict


def get_binned_occurrences(context: Context) -> ActiveEvents:
    """
    Calculates the active events for weekly, monthly and yearly bins.
    :param context: contains precalculated data.
    :return: The calculated active events.
    """
    data = context.data
    active_event_parameters = context.active_event_parameters if context.active_event_parameters else (
        ActiveEventParameters(positive_events=[],
                              negative_events=[],
                              singular_events=list(data["concept:name"].unique())))
    initial_timestamp = data["time:timestamp"].min()
    final_timestamp = data["time:timestamp"].max()
    active_events = ActiveEvents(
        yearly=calculate_bin_values(data, calculate_yearly_bins(initial_timestamp, final_timestamp),
                                    active_event_parameters),
        monthly=calculate_bin_values(data, calculate_monthly_bins(initial_timestamp, final_timestamp),
                                     active_event_parameters),
        weekly=calculate_bin_values(data, calculate_weekly_bins(initial_timestamp, final_timestamp),
                                    active_event_parameters))
    return active_events


def get_n_traces(context: Context) -> int:
    """
    Calculates the total number of traces in the dataset
    :param context:
    :return: number of traces.
    """
    return int(context.data["case:concept:name"].nunique())


def get_n_events(context: Context) -> int:
    """
    Calculates the total number of events in the dataset.
    :param context:
    :return: number of events.
    """
    return len(context.data)


def get_n_variants(context: Context) -> int:
    """
    Calculates the total number of variants in the dataset.
    :param context:
    :return: number of variants.
    """
    return len(context.variants)


def get_top_variants(context: Context) -> dict[str, TopVariant]:
    """
    Creates a dict with the ranking as key and the events defining this variant as value from the top variants provided.
    :param context:
    :return: dict.
    """
    top_variants = context.top_variants
    top_variants_dict = {}
    grouped_data = context.grouped_data
    agg_data = grouped_data.agg({"concept:name": list, "time:timestamp": list})
    agg_data["diff"] = pd.to_timedelta(
        agg_data["time:timestamp"].str[-1] - agg_data["time:timestamp"].str[0]).dt.total_seconds()
    for index, variant in enumerate(top_variants):
        current: TopVariant = TopVariant(event_sequence=list(variant[0]), frequency=variant[1],
                                         mean_duration=agg_data[agg_data["concept:name"].isin([list(variant[0])])][
                                             "diff"].mean())
        top_variants_dict[str(index)] = current
    return top_variants_dict


metrics = {
    "n_traces": get_n_traces,
    "n_events": get_n_events,
    "n_variants": get_n_variants,
    "top_variants": get_top_variants,
    "tbe": get_time_between_events,
    "max_trace_length": get_max_trace_length,
    "min_trace_length": get_min_trace_length,
    "event_frequency_distr": get_event_frequency_distribution,
    "trace_length_distr": get_trace_length_distribution,
    "max_trace_duration": get_max_trace_duration,
    "min_trace_duration": get_min_trace_duration,
    "active_events": get_binned_occurrences

}


def get_metrics(data: pd.DataFrame, active_event_parameters: ActiveEventParameters | None,
                n_top_variants: int) -> Metrics:
    """
    Calculates the metrics for a given dataset.
    :param active_event_parameters: Parameters to calculate the active events per timeframe.
    :param data: Data from which the metrics are calculated.
    Should have three columns, 'case:concept:name', 'concept:name' and 'time:timestamp'.
    :param n_top_variants: Amount of top variants that should be included in the variant dependent metrics.
    :return: calculated metrics.
    """
    grouped_data = data.groupby("case:concept:name", as_index=False)
    variants: dict[list[str], int] = get_variants_count(data)
    top_variants: list[tuple[list[str], int]] = list(sorted(variants.items(), key=lambda item: item[1], reverse=True))[
        0:n_top_variants]
    context = Context(data=data,
                      grouped_data=grouped_data,
                      active_event_parameters=active_event_parameters,
                      variants=variants,
                      top_variants=top_variants
                      )
    values = {
        field: None if field in CONFIG["exclude"]
        else metrics[field](context)
        for field in Metrics.model_fields.keys()
    }
    return Metrics.model_validate(values)
