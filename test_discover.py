import json
from collections import Counter

import requests

with open("test_logs/sepsis.json") as f:
    json_data = json.load(f)

event_names = list(json_data.get("concept:name", {}).values())
top_events = [name for name, _ in Counter(event_names).most_common(3)]

payload = {
    "data": json_data,
    "parameters": {
        "active_events": {
            "positive_events": [],
            "negative_events": [],
            "singular_events": top_events,
        },
        "n_top_variants": 10,
        "reduce_complexity_by": 0,
        "add_counts": False,
        "state_changing_events": None,
    },
    "callback_url": None,
    "id": "test-sepsis",
}

r = requests.post("http://localhost:8000/discover", json=payload, timeout=120)
r.raise_for_status()
print(r.json())
