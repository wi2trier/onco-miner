import numpy as np
import pandas as pd
import pm4py
import pytz
from dateutil.relativedelta import relativedelta
from pandas.core.groupby import DataFrameGroupBy
from pm4py.statistics.variants.pandas.get import get_variants_count

from input_model import ActiveEventParameters
from response_model import ActiveEvents, Connection, Metrics

utc = pytz.UTC


def get_time_between_events(top_variants: list[tuple[list[str], int]], data: pd.DataFrame,
                            grouped_data: pd.DataFrame) -> \
        list[Connection]:
    """
    calculates statistics regarding the time between events of the top variants.
    :param grouped_data: data grouped by 'case:concept:name' with 'concept:name' as list.
    :param top_variants: list of the top variants with their frequency.
    :param data: data on which grouped data is based.
    :return: list of edges with statistics between events of the top variants.
    """
    top_variants_list = [list(x[0]) for x in top_variants]
    relevant_traces = grouped_data[grouped_data["concept:name"].isin(top_variants_list)]["case:concept:name"]
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


def get_trace_lengths(data: pd.DataFrame) -> tuple[int, int]:
    """
    Calculates the amount of traces for the trace with the most and the least events in the data.
    :param data: data to be used to calculate the lengths.
    :return: tuple of minimum trace length, maximum trace length.
    """
    trace_lengths = data["case:concept:name"].value_counts()
    return trace_lengths.min(), trace_lengths.max()


def get_trace_durations(grouped_data:  DataFrameGroupBy) -> tuple[float, float]:
    """
    Calculates the time delta between start and end of the traces
    with the maximum and minimum time delta respectively in the data.
    :param grouped_data: data grouped by 'case:concept:name' with 'concept:name' as list.
    :return: tuple of minimum time delta , maximum time delta in seconds.
    """

    min_values = grouped_data.min()["time:timestamp"]
    max_values = grouped_data.max()["time:timestamp"]
    difference = max_values - min_values
    return difference.min().total_seconds(), difference.max().total_seconds()


def get_event_frequency_distribution(data: pd.DataFrame) -> dict[str, int]:
    """
    Calculates the frequency of each event in the data.
    :param data: Dataframe with 'concept:name' containing the event names.
    :return: Dictionary with event as key and frequency as value.
    """
    return data["concept:name"].value_counts().to_dict()


def get_trace_length_distribution(data: pd.DataFrame) -> dict[str, int]:
    """
    Calculates how often each trace length occurred.
    :param data: Dataframe with 'case:concept:name' containing the trace names.
    :return: Dictionary with length as key and frequency as value.
    """
    return data["case:concept:name"].value_counts().astype(str).value_counts().to_dict()


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


def get_binned_occurrences(data: pd.DataFrame, active_event_parameters: ActiveEventParameters) -> ActiveEvents:
    """
    Calculates the active events for weekly, monthly and yearly bins.
    :param active_event_parameters: Parameters to calculate the active events per timeframe.
    :param data: Data from which the active events as well as the timestamps are calculated.
    :return: The calculated active events.
    """
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


def get_metrics(data: pd.DataFrame, active_event_parameters: ActiveEventParameters,
                n_top_variants: int = 10) -> Metrics:
    """
    Calculates the metrics for a given dataset.
    :param active_event_parameters: Parameters to calculate the active events per timeframe.
    :param data: Data from which the metrics are calculated.
    Should have three columns, 'case:concept:name', 'concept:name' and 'time:timestamp'.
    :param n_top_variants: Amount of top variants that should be included in the variant dependent metrics.
    :return: calculated metrics.
    """
    grouped_data = data.groupby("case:concept:name", as_index=False)
    aggregated_data = grouped_data.agg({"concept:name": list, "time:timestamp": list})
    variants: dict[list[str], int] = get_variants_count(data)
    top_variants: list[tuple[list[str], int]] = list(sorted(variants.items(), key=lambda item: item[1], reverse=True))[
        0:n_top_variants]
    top_variants_dict = {}
    tbe = get_time_between_events(top_variants, data, aggregated_data)
    min_trace_length, max_trace_length = get_trace_lengths(data)
    min_trace_duration, max_trace_duration = get_trace_durations(grouped_data)

    for index, variant in enumerate(top_variants):
        top_variants_dict[str(index)] = list(variant[0])
    metrics = Metrics(n_cases=data["case:concept:name"].nunique(), n_events=len(data), n_variants=len(variants),
                      top_variants=top_variants_dict, tbe=tbe, max_trace_length=max_trace_length,
                      min_trace_length=min_trace_length,
                      event_frequency_distr=get_event_frequency_distribution(data),
                      trace_length_distr = get_trace_length_distribution(data),
                      max_trace_duration=max_trace_duration, min_trace_duration=min_trace_duration,
                      active_events=get_binned_occurrences(data, active_event_parameters))
    return metrics
