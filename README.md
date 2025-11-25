# onco-miner

> **Process mining for oncology** — a backend module that takes **pre-filtered** oncology event data (e.g., oBDS from German cancer registries) and performs **process discovery** and **performance analysis** for dashboarding and research reuse.

---

<p align="center">
  <img src="https://img.shields.io/badge/status-pre--alpha-inactive" alt="Status: pre-alpha"/>
  <img src="https://img.shields.io/badge/domain-oncology-blue" alt="Domain: Oncology"/>
  <img src="https://img.shields.io/badge/process--mining-enabled-brightgreen" alt="Process Mining: enabled"/>
  <img src="https://img.shields.io/badge/license-GNU%20GPL%20v3.0-orange" alt="License: GPL v3.0"/>
</p>

---

## What it does (scope)

- **Process discovery** on **already filtered** oncology event data  
- **Performance analysis** (e.g., frequencies, durations, throughput, ...)   

---

## Why it exists

Transparent and reproducible analysis of real oncology care pathways helps improve quality and equity of care through data exploration. **onco-miner** focuses on the mining and analysis layer only, so it can plug into different data providers and dashboards without owning data preparation.

---

## Technical Details

### Expected input Format

The data should be provided as a json dict with the following structure:

Each event should have an index, a trace name, an event name and a time stamp in the ISO8601 standard.

The data in the following Example consists of two traces, "Trace1" and "Trace2".
"Trace1" consists of two events, "EventA" (2025-10-17T11:45:23Z) and "EventB" (2025-10-18T23:48:05Z).
"Trace2" consists of one event, "EventB" (2024-08-12T08:27:12Z).

    {
        "concept:name": 
        {
            "1": "EventA",
            "2": "EventB",
            "3": "EventB"
        },
        "case:concept:name":
        {
            "1": "Trace1",
            "2": "Trace1",
            "3": "Trace2"
        },
        "time:timestamp":
        {
            "1": "2025-10-17T11:45:23Z",
            "2": "2025-10-18T23:48:05Z",
            "3": "2024-08-12T08:27:12Z"
        }
    }

### Output Format

    {
        "graph":
        {
            "connections":
            [
                {
                    "e1": str,
                    "e2": str,
                    "frequency": int,
                    "median": float,
                    "min": float,
                    "max": float,
                    "stdev": float,
                    "sum": float,
                    "mean": float
                }
            ]
            "start nodes":
            {
                "{event_name}": int
            },
            "end nodes":
            {
                "{event_name}": int
            },
        }
        "metrics":
        {
            "n_cases": int,
            "n_events": int,
            "n_variants": int,
            "top_variants":
            {
                "{rank}": [str]
            },
            "tbe":
            [
                {
                    "e1": str,
                    "e2": str,
                    "time": str
                }
            ],
            "events_p_timeframe":
            {
                "{start_time}": int
            },
            "max_trace_length": int,
            "min_trace-length": int,
            "event_frequency_distr":
            {
                "{event_name}": int,
            }
        }
        "created": str,
        "id": str
    }

