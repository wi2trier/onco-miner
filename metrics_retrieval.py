from datetime import timedelta, datetime

import numpy as np
import pandas as pd
import pm4py
import pytz
from dateutil.relativedelta import relativedelta
from pm4py.statistics.variants.pandas.get import get_variants_count


utc = pytz.UTC


from response_model import Metrics, Connection, ActiveEvents


def get_time_between_events(top_variants, data: pd.DataFrame, grouped_data: pd.DataFrame) -> list[Connection]:
    """
    To work, the given dataframe needs to already be sorted!
    Sorting it again could lead to inconsistencies due to events occurring at the same time.
    :param grouped_data:
    :param top_variants:
    :param data:
    :return:
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


def get_trace_lengths(grouped_data: pd.DataFrame) -> tuple[int, int]:
    trace_lengths = grouped_data["concept:name"].apply(lambda x: len(x))
    return trace_lengths.min(), trace_lengths.max()


def get_trace_durations(grouped_data: pd.DataFrame) -> tuple[float, float]:
    trace_durations = grouped_data["time:timestamp"].apply(lambda x: x[-1] - x[0])
    return trace_durations.min().total_seconds(), trace_durations.max().total_seconds()


def get_event_frequency_distribution(data: pd.DataFrame) -> dict[str, int]:
    return data["concept:name"].value_counts().to_dict()


def calculate_weekly_bins(initial_timestamp: datetime, final_timestamp: datetime) -> list[datetime]:
    start_of_week = initial_timestamp - timedelta(days=initial_timestamp.weekday())
    start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    week_starts = [start_of_week]
    while start_of_week <= final_timestamp:
        week_starts.append(start_of_week)
        start_of_week = start_of_week + timedelta(days=7)
    return week_starts


def calculate_monthly_bins(initial_timestamp: datetime, final_timestamp: datetime) -> list[datetime]:
    start_of_month = initial_timestamp - timedelta(days=initial_timestamp.day - 1)
    start_of_month.replace(hour=0, minute=0, second=0, microsecond=0)
    month_starts = [start_of_month]
    while start_of_month <= final_timestamp:
        month_starts.append(start_of_month)
        start_of_month = start_of_month + relativedelta(months=1)
    return month_starts


def calculate_yearly_bins(initial_timestamp: datetime, final_timestamp: datetime) -> list[datetime]:
    start_of_year = datetime(initial_timestamp.year, 1, 1).replace(tzinfo=utc)
    year_starts = []
    while start_of_year <= final_timestamp:
        year_starts.append(start_of_year)
        start_of_year = start_of_year + relativedelta(years=1)
    return year_starts


def calculate_bin_values(data: pd.DataFrame, bin_starts: list[datetime]) -> dict[str, int]:
    positive_events = []
    negative_events = []
    singular_events = []
    bin_dict = {}
    n_bins = len(bin_starts)
    active_events = 0
    for i, bin_start in enumerate(bin_starts):
        bin_end = bin_starts[i + 1] if i < n_bins - 1 else datetime.now().replace(tzinfo=utc)
        pre_bin_start = bin_starts[i - 1] if i > 0 else bin_start - timedelta(days=1)
        bin_data = data[data["time:timestamp"].between(bin_start, bin_end, inclusive="left")]
        pre_bin_data = data[data["time:timestamp"].between(pre_bin_start, bin_start, inclusive="left")]
        active_events += len(bin_data[bin_data["concept:name"].isin(positive_events)]) - len(
            pre_bin_data[pre_bin_data["concept:name"].isin(negative_events)])
        amount = active_events + len(bin_data[bin_data["concept:name"].isin(singular_events)])
        bin_dict[str(bin_start)] = amount
    return bin_dict


def get_binned_occurrences(data: pd.DataFrame) -> ActiveEvents:
    initial_timestamp = data["time:timestamp"].min()
    final_timestamp = data["time:timestamp"].max()
    return ActiveEvents(yearly=calculate_bin_values(data, calculate_yearly_bins(initial_timestamp, final_timestamp)),
                        monthly=calculate_bin_values(data, calculate_monthly_bins(initial_timestamp, final_timestamp)),
                        weekly=calculate_bin_values(data, calculate_weekly_bins(initial_timestamp, final_timestamp)))


def get_metrics(data: pd.DataFrame, n_top_variants: int = 10) -> Metrics:
    grouped_data = data.groupby("case:concept:name", as_index=False).agg({"concept:name": list, "time:timestamp": list})
    variants = get_variants_count(data)
    top_variants = list(sorted(variants.items(), key=lambda item: item[1], reverse=True))[0:n_top_variants]
    top_variants_dict = {}
    tbe = get_time_between_events(top_variants, data, grouped_data)
    min_trace_length, max_trace_length = get_trace_lengths(grouped_data)
    min_trace_duration, max_trace_duration = get_trace_durations(grouped_data)

    for index, variant in enumerate(top_variants):
        top_variants_dict[str(index)] = list(variant[0])
    metrics = Metrics(n_cases=data["case:concept:name"].nunique(), n_events=len(data), n_variants=len(variants),
                      top_variants=top_variants_dict, tbe=tbe, max_trace_length=max_trace_length,
                      min_trace_length=min_trace_length,
                      event_frequency_distr=get_event_frequency_distribution(data),
                      max_trace_duration=max_trace_duration, min_trace_duration=min_trace_duration,
                      active_events=get_binned_occurrences(data))
    return metrics
