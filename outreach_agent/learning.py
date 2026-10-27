"""Transparent relationship outcome analytics; suggestions never silently change weights."""
from collections import Counter, defaultdict

POSITIVE = {"REPLIED","MEETING","INTRODUCTION","OPPORTUNITY","HIRED"}
def summarize(event_counts, min_contacted=10):
    """Aggregate counts by geographic segment; no profiling of individuals."""
    groups=defaultdict(Counter)
    for item in event_counts:
        groups[item["segment"]][item["kind"]] += int(item["n"])
    output=[]
    for segment, events in sorted(groups.items()):
        sent=events["CONTACTED"]
        replies=events["REPLIED"]
        meetings=events["MEETING"]
        introductions=events["INTRODUCTION"]
        # Rates are descriptive, NOT conversion forecasts or causal effects.
        output.append({
            "segment":segment, "actual_contacts":sent, "replies":replies,
            "meetings":meetings, "introductions":introductions,
            "observed_reply_rate":round(replies/sent,3) if sent else None,
            "sample_sufficient": sent >= min_contacted,
            "recommendation": ("Insufficient actual contacts for a trend; do not adjust ranking"
                if sent < min_contacted else
                "Human-review geography/source strategy using observed results; no automatic weight changes")
        })
    return {"segments":output, "weight_changes_applied":0,
            "caveats":["Only manually recorded outcomes are counted.",
                       "Contacted people are a self-selected sample; not causal or predictive.",
                       "No autonomous optimization or change to eligibility gates."]}
