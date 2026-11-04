"""DISPOSABLE WINDOWS GUEST ONLY: synthetic M2 relationship + source packet fixture.

Never use against a real CareerOutreach folder. The CLI refuses non-Windows
and requires the guest marker/env from the guarded owner PowerShell seeder.
No live data is read, no web calls occur, and no authorization is granted.
"""
from __future__ import annotations

import argparse
from datetime import date
import json
import os
from pathlib import Path
from uuid import uuid4

from outreach_agent.state import PrivateStore
from outreach_agent.career_contribution import validate_v22_packet
from scripts.assess_career_opportunities_v22 import assess_v22_packet


def _claim(prefix, kind, subject, object_id=None):
    text = "Example Domain"
    return {
        "claim_id": prefix, "claim_type": kind, "claim_text": text,
        "source_url": "https://example.com/",
        "publisher": "Example Domain (TECHNICAL TEST, not a career employer)",
        "source_origin_id": "example-com-m2-technical-fixture",
        "retrieved_at": date.today().isoformat(),
        "published_on": date.today().isoformat(),
        "excerpt": text, "page_read_success": True,
        "support_relationship": "DIRECT", "subject_id": subject,
        "object_id": object_id,
    }


def _opportunity(index: int, name: str) -> dict:
    org_id = "m2-technical-only-org"
    initiative_id = f"m2-initiative-{index}"
    person_id = f"m2-synthetic-person-{index}"
    oid = f"obj-{index}"
    role = f"role-{index}"
    owner = f"owner-{index}"
    problem = f"problem-{index}"
    trigger = f"trigger-{index}"
    return {
        "schema_version": "2.2", "project_id": "PERSONAL_CAREER_OUTREACH",
        "purpose": "Synthetic owner handoff qualification, NO actual career opportunity",
        "engagement_pathway": "STRATEGIC_EXPLORATION",
        "capability_theme": "ENTERPRISE_PRODUCT_LEADERSHIP",
        "organization": {"organization_id": org_id,
                         "name": "M2 Synthetic Technical Employer — NOT REAL",
                         "work_mode": "TUCSON", "feasible": True},
        "initiative": {"initiative_id": initiative_id, "objective_claim_id": oid},
        "claims": [
            _claim(oid, "BUSINESS_OBJECTIVE", org_id),
            _claim(role, "CURRENT_EXECUTIVE_ROLE", person_id, org_id),
            _claim(owner, "EXECUTIVE_OWNERSHIP", person_id, initiative_id),
            _claim(problem, "OPERATIONAL_PROBLEM", org_id, initiative_id),
            _claim(trigger, "BUSINESS_TRIGGER", org_id),
        ],
        "contribution": {
            "business_objective_claim_id": oid,
            "candidate_basis": "Synthetic product leadership fixture, never actual candidate assurance",
            "candidate_claim_approved": True,
            "proposed_value": "Synthetic process review only; do not approach a person",
            "mandate_key": f"m2-mandate-{index}",
            "leadership_need_assumed": False, "hiring_claim": False,
        },
        "executive": {
            "person_id": person_id, "name": name, "current_role_claim_id": role,
            "opted_out": False,
            "ownership": {"role_type": "BUSINESS_OUTCOME_OWNER",
                          "ownership_grade": "DOCUMENTED", "claim_id": owner},
            "route": {"route_type": "NO_ROUTE", "verified_for_person": False},
        },
        "job": None,
        "career_value": {
            "business_decision": "Synthetic process decision, without real employer business need",
            "proposed_internal_responsibility":
                "Synthetic portfolio prioritization responsibility, no actual job or outreach",
            "candidate_evidence_refs": ["MOBIUS_PRODUCT_PORTFOLIO"],
            "complementary_scope":
                "Technical test of independent responsibility and ownership boundary",
            "existing_owner_status": "OWNER_RESEARCHED_NOT_FOUND",
            "expected_outcome":
                "Demonstrate only reproducible technical owner review handoff",
            "limitations": "This is a mock employer fixture, never a real opportunity",
            "trigger_claim_id": trigger, "maturity": "PILOTED",
            "problem_claim_id": problem,
            "outcome_metric": "Technical fixture validation count",
            "mandate_boundary": "COMPLEMENTARY_INTERNAL_SCOPE",
        },
    }


def seed_synthetic_fixture(root: Path, state_key, identity_key) -> dict:
    """Only create new files in a new guest folder; must not touch existing files."""
    root = Path(root).resolve()
    db = root / "relationships.sqlite"
    runs = root / "runs"
    packet_path = runs / "m2-synthetic-packet.json"
    report_path = runs / "m2-synthetic-report.json"
    if any(p.exists() for p in (db, packet_path, report_path)):
        raise FileExistsError("M2_FIXTURE_MUST_NOT_OVERWRITE_EXISTING_FILES")
    runs.mkdir(parents=True, exist_ok=True)
    writer = PrivateStore(db, key=state_key, identity_key=identity_key)
    try:
        writer.remember_relationship(
            "Pat Example", "PREVIOUSLY_MET",
            profile_url="https://example.org/professional/pat-one")
        writer.remember_relationship(
            "Alex Example", "FIRST_LEARNED",
            profile_url="https://example.org/professional/alex")
        writer.remember_relationship(
            "Jordan Example", "PREVIOUSLY_MET",
            profile_url="https://example.org/professional/jordan")
        person = writer.match({"person_name": "Jordan Example"})[0]
        writer.record_event(person["person_id"], "OPTED_OUT")
    finally:
        writer.close()
    packet = {
        "schema_version": "2.2", "project_id": "PERSONAL_CAREER_OUTREACH",
        "run_id": "m2-guest-" + uuid4().hex,
        "date_local": date.today().isoformat(),
        "opportunities": [
            _opportunity(0, "Pat Example"),
            _opportunity(1, "Pat Example"),
            _opportunity(2, "Jordan Example"),
            _opportunity(3, "Alex Example"),
        ],
    }
    validate_v22_packet(packet)
    report = assess_v22_packet(packet)
    if report["contact_ready"] != 0 or report["send_authorized"] is not False:
        raise ValueError("UNEXPECTED_ACTION_AUTHORITY_IN_M2_FIXTURE")
    for path, value in ((packet_path, packet), (report_path, report)):
        with path.open("x", encoding="utf-8") as stream:
            json.dump(value, stream, indent=2, ensure_ascii=False, sort_keys=True)
            stream.write("\n")
    return {
        "fixture_only": True, "people_seeded": 3, "opportunities_seeded": 4,
        "packet_path": str(packet_path), "report_path": str(report_path),
        "source_truth_independently_verified": False,
        "contact_ready": 0, "send_authorized": False,
        "application_submitted": False,
    }


def verify_restored_fixture(restored_db: Path, state_key, identity_key) -> dict:
    """READ ONLY: prove recovered synthetic identities and opt-out are intact."""
    db = Path(restored_db).resolve()
    if not db.is_file():
        raise FileNotFoundError("M2_RESTORED_DB_NOT_FOUND")
    store = PrivateStore(db, key=state_key, identity_key=identity_key, read_only=True)
    try:
        met = store.check_relationship(
            "Pat Example", profile_url="https://example.org/professional/pat-one")
        namesake = store.check_relationship(
            "Pat Example", profile_url="https://example.org/professional/pat-other")
        seen = store.check_relationship(
            "Alex Example", profile_url="https://example.org/professional/alex")
        opted_out = store.check_relationship(
            "Jordan Example", profile_url="https://example.org/professional/jordan")
        if (met["result"] != "EXISTING_RELATIONSHIP"
                or namesake["result"] != "POSSIBLE_NAMESAKE_HOLD"
                or seen["result"] != "SEEN_IN_STORE"
                or opted_out["suppressed"] is not True
                or any(row["granted_contact_readiness"] for row in
                       (met, namesake, seen, opted_out))):
            raise ValueError("M2_RESTORED_IDENTITY_OR_SUPPRESSION_MISMATCH")
    finally:
        store.close()
    return {"restored_memory_verified": True,
            "previously_met": "EXISTING_RELATIONSHIP",
            "namesake": "POSSIBLE_NAMESAKE_HOLD",
            "first_learned": "SEEN_IN_STORE",
            "opt_out": "SUPPRESSED",
            "read_only": True,
            "contact_ready": False, "send_authorized": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--private-root", required=True)
    parser.add_argument("--verify-restored", default=None,
                        help="Read-only restored synthetic database; must be below guest backup folder")
    args = parser.parse_args()
    # This is NOT a VM attestation. The separate interactive PS script checks
    # guest model, guest marker, and requires explicit owner confirmation.
    if os.name != "nt" or os.environ.get("CAREER_M2_DISPOSABLE_VM_CONFIRMED") != "YES":
        raise RuntimeError("M2_GUEST_OWNER_INTERACTIVE_SEED_ONLY")
    expected = (Path(os.environ["LOCALAPPDATA"]) / "CareerOutreach").resolve()
    target = Path(args.private_root).resolve()
    if target != expected:
        raise ValueError("M2_GUEST_PRIVATE_FOLDER_MISMATCH")
    key = os.environ.get("OUTREACH_STATE_KEY")
    identity = os.environ.get("OUTREACH_IDENTITY_KEY")
    if not key or not identity:
        raise RuntimeError("M2_GUEST_SYNTHETIC_KEYS_REQUIRED")
    if args.verify_restored:
        recovered = Path(args.verify_restored).resolve()
        backup_root = (target / "backups").resolve()
        if backup_root not in recovered.parents:
            raise ValueError("M2_RESTORED_DB_MUST_BE_UNDER_GUEST_BACKUPS")
        print(json.dumps(verify_restored_fixture(recovered, key, identity), indent=2))
    else:
        print(json.dumps(seed_synthetic_fixture(target, key, identity), indent=2))


if __name__ == "__main__":
    main()
