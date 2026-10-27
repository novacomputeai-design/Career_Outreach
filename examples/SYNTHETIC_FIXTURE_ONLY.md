# Synthetic candidate contract (NOT a real leader)
To test the offline validator, create a PRIVATE JSON array with entries shaped like the example below and a PRIVATE history JSON array. Do not check these into a public repo when they contain actual people.

```json
[
  {
    "person_id": "synthetic-person-1",
    "person_name": "Example Executive",
    "organization": "Example Organization",
    "current_title": "VP, Product",
    "role_source_url": "https://example.org/team",
    "reason_source_url": "https://example.org/initiatives",
    "contact_route_url": "https://example.org/contact",
    "route_type": "INDIRECT",
    "role_verified": true,
    "contact_route_verified": true,
    "history_checked": true,
    "novelty": "NEW",
    "suppressed": false,
    "observed_on": "2026-10-27",
    "why_connect": "A specific discussion about verified enterprise platform modernization work.",
    "scores": {"alignment": 25, "influence": 20, "conversation": 18, "reachability": 12, "geography": 8}
  }
]
```

Use `python scripts/qualify_candidates.py --candidates private/candidates.json --history private/history.json --output reports/brief.json`. The script checks structure/threshold/dedup only: it **does not visit the source URLs, verify that the contacts exist, send messages, or maintain live CRM state**. A true agent runtime must independently validate the source facts and state assertions before presenting any person as contact-ready.
