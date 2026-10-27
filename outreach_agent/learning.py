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

def propose_strategy(event_counts,min_contacted=10):
    """Evidence-derived human REVIEW suggestion, never autonomous adaptation."""
    from collections import defaultdict,Counter
    groups=defaultdict(Counter)
    for item in event_counts:
        groups[item["segment"]][item["kind"]]+=int(item["n"])
    eligible={k:v for k,v in groups.items() if v["CONTACTED"]>=min_contacted and k in ("tucson","remote")}
    if len(eligible)<2:
        return {"status":"INSUFFICIENT_COMPARABLE_DATA","proposed_priority":None,
                "approved":False,"note":"Both geographic groups need at least 10 observed contacts"}
    a={k:(v["REPLIED"]/v["CONTACTED"]) for k,v in eligible.items()}
    top=max(a,key=a.get)
    if max(a.values())-min(a.values())<0.05:
        return {"status":"NO_ACTIONABLE_DIFFERENCE","proposed_priority":None,"approved":False,
                "observed_reply_rates":a}
    return {"status":"HUMAN_REVIEW_ONLY","proposed_priority":top,"approved":False,
            "observed_reply_rates":a,
            "note":"Observational, self-selected results are not causal. Do not automatically adjust searches."}
