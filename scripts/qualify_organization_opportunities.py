#!/usr/bin/env python3
"""Owner/Codex public-only research: assess V1.1 employer opportunity packet.

Never reads DPAPI, private relationships, Google Drive or sends outreach.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from outreach_agent.opportunity_packet import assess_private_file


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", required=True, help="New public-research JSON OUTSIDE Git")
    ap.add_argument("--output", required=True, help="Unused report JSON OUTSIDE Git")
    ap.add_argument("--pilot-size", type=int, default=5)
    args = ap.parse_args()
    if not 1 <= args.pilot_size <= 20:
        ap.error("--pilot-size must be 1..20")
    report = assess_private_file(args.input, args.output, pilot_size=args.pilot_size)
    print(json.dumps({
        "status": "V1_1_PUBLIC_OPPORTUNITY_PRECHECK_COMPLETE",
        "run_id": report["run_id"],
        "opportunities_researched": report["opportunities_researched"],
        "shortlisted_for_review": report["portfolio"]["shortlisted_for_review"],
        "research_shortfall": report["portfolio"]["shortfall"],
        "new_contact_ready": 0, "send_authorized": False,
        "warning": "Human source truth, hiring and private novelty remain unverified."
    }, indent=2))


if __name__ == "__main__":
    main()
