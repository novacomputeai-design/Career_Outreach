#!/usr/bin/env python3
"""Owner-only review handoff: PUBLIC candidate names + minimal private classification.

Run ONLY in ordinary operator PowerShell, never inside Codex. Input/output
must remain outside the public Git checkout. Never loads DPAPI/keys, no
database access, no sending, and no contact-ready promotions.
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from outreach_agent.operator_handoff import reconcile_operator_screening


def private_json(path: str, *, exists: bool) -> Path:
    p = Path(path).expanduser().resolve()
    if p == ROOT or ROOT in p.parents:
        raise ValueError("Private handoff files must be outside the public repository")
    if p.suffix.lower() != ".json":
        raise ValueError("Only .json handoff files are accepted")
    if exists:
        if not p.is_file() or p.stat().st_size > 65536:
            raise ValueError("Missing or oversized private handoff input (64 KiB limit)")
    elif p.exists():
        raise FileExistsError("Never overwrite an existing private handoff file")
    return p


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", required=True,
                        help="Owner-supplied public research names/profile list outside Git")
    parser.add_argument("--screening", required=True,
                        help="Owner-run private batch output outside Git")
    parser.add_argument("--output", required=True,
                        help="New private minimal reconciliation report outside Git")
    args = parser.parse_args()
    candidates = private_json(args.candidates, exists=True)
    screening = private_json(args.screening, exists=True)
    output = private_json(args.output, exists=False)
    if len({candidates, screening, output}) != 3:
        raise ValueError("Input and output paths must be distinct")
    data = json.loads(candidates.read_text(encoding="utf-8-sig"))
    response = json.loads(screening.read_text(encoding="utf-8-sig"))
    result = reconcile_operator_screening(data, response)
    output.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive create prevents silently modifying or replacing private files.
    with output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    if os.name == "posix":
        output.chmod(0o600)
    print(json.dumps({
        "status": "OWNER_RECONCILIATION_REPORT_CREATED",
        "project_id": result["project_id"],
        "people_reconciled": result["people_reconciled"],
        "new_contact_ready": 0, "send_authorized": False,
        "warning": "Operator manual review only; no cross-channel novelty proof.",
    }, indent=2))


if __name__ == "__main__":
    main()
