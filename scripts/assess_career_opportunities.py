#!/usr/bin/env python3
"""Offline V2.1 organization research preflight; no web, memory, Drive or sending."""
from __future__ import annotations
import argparse
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from outreach_agent.career_intelligence_packet import assess_private_files


def main():
    parser = argparse.ArgumentParser(description="Validate a V2.1 public-only career research packet")
    parser.add_argument("--input", required=True, help="Private JSON outside the public checkout")
    parser.add_argument("--out", required=True, help="Unused private output JSON outside the public checkout")
    args = parser.parse_args()
    result = assess_private_files(args.input, args.out)
    print("V2.1 RESEARCH REVIEW ONLY — no independent source verification or external actions")
    print("Organizations/opportunities:", result["research_summary"]["reviewed"])
    print("States:", result["research_summary"]["research_states"])
    print("Identity holds:", len(result["research_summary"]["identity_holds"]))
    print("Native skills: NOT_VERIFIED. Private history: UNCHECKED. CONTACT_READY: 0. SENT: 0.")


if __name__ == "__main__":
    main()
