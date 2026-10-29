#!/usr/bin/env python3
"""Export a Codex public-only Fadi research packet to local review CSVs.

No Google API, no private SQLite, no DPAPI, no sender. The owner reviews and
imports rows to the private Google Sheet; never consider CSV an approval.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from outreach_agent.drive_review_packet import read_input,write_review_packet


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",required=True,help="Research-only JSON outside public repository")
    parser.add_argument("--out-dir",required=True,help="Unused private folder for review packet")
    args=parser.parse_args()
    manifest=write_review_packet(read_input(args.input),Path(args.out_dir))
    print(json.dumps({"status":"UNSENT_DRIVE_REVIEW_PACKET_PREPARED",**manifest},indent=2))


if __name__=="__main__":
    main()
