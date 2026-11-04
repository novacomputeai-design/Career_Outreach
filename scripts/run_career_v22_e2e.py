"""Execute bounded synthetic V2.2 cases through the public packet CLI.

The static 54-case inventory is intentionally immutable. This runner writes a
separate register and per-case CLI input/output artifacts outside the repo.
Synthetic PASS is never host, source-truth, or production qualification.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import date, timedelta, datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "evals" / "career_v22_e2e_matrix.json"
CLI = ROOT / "scripts" / "assess_career_opportunities_v22.py"
HARNESS_FILES = (Path(__file__), ROOT / "tests" / "test_career_v22_e2e_runner.py")
HOLD_BLOCKERS = {
    "E2E-03": "The case's prestige-only semantics are not represented by a structured field or deterministic evaluator rule; current blank-field probe is schema-invalid.",
    "E2E-04": "The synthetic strategic packet schema has no direct-hiring location-exclusion assertion; needs a contract-valid ATS fixture and evaluator assertion.",
    "E2E-05": "Transferability across industries and regulated-domain qualification are owner-judgment questions; the packet only supports approved evidence references and limitation text.",
    "E2E-06": "No single evaluator assertion compares capability theme independently across both hiring pathways.",
    "E2E-08": "Maturity is a caller-provided enum; no source-backed progression or contradiction oracle exists in the current CLI.",
    "E2E-11": "Generic-pitch semantics are not assessed by the deterministic evaluator; current prose fields have no specific-value quality oracle.",
    "E2E-15": "Role seniority versus hands-on engineering is not reliably classified from free-text responsibility by the current evaluator.",
    "E2E-19": "Exact string reproduction cannot independently establish the semantic meaning of a claim; requires human source interpretation.",
    "E2E-20": "Syndicated-source independence requires origin-level corroboration outside this one-packet CLI.",
    "E2E-21": "Historical biography versus later departure requires independently dated executive-affiliation source assessment.",
    "E2E-22": "Past affiliation at another employer needs an independently corroborated cross-employer identity history.",
    "E2E-23": "Namesake collision requires trusted person identity history, beyond source-claimed current-role records.",
    "E2E-26": "Agreement versus legal transaction close requires independently read transaction source and event chronology.",
    "E2E-27": "Employer announcement versus observed program outcome requires independent outcome evidence.",
    "E2E-29": "Absent requisition in a later run needs two-run private public-ledger continuity execution.",
    "E2E-30": "Closed vacancy plus an independent strategic mandate needs a multi-opportunity cross-run fixture.",
    "E2E-31": "Historical record preservation through source outage needs prior immutable ledger and recovery fixture.",
    "E2E-34": "Domain-specific eligibility and transferrable director responsibilities need source evidence and owner judgment.",
    "E2E-35": "PURSUE is an owner-only preference; the public CLI cannot execute or authenticate owner decision behavior.",
    "E2E-36": "REJECT reason retention needs a trusted owner-only signed feedback journal test.",
    "E2E-37": "Policy/code/schema state equivalence is checked by a separate validator, not this packet CLI.",
    "E2E-38": "Legacy runner version separation requires execution of both V2.1 and V2.2 interfaces.",
    "E2E-41": "Missing protected relationship memory can only be qualified in an isolated owner-controlled recovered test copy.",
    "E2E-42": "Known person plus new employer opportunity needs trusted private-history classification without suppression of opportunity.",
    "E2E-45": "Prompt injection from a real untrusted webpage requires observable host/tool behavior; the CLI does not browse.",
    "E2E-46": "Exact draft Gate A versus separate send Gate B needs authenticated operator-side enforcement, not offline research fields.",
    "E2E-48": "Interruption recovery with no duplicate writes needs a two-run ledger and restart-failure rehearsal.",
    "E2E-49": "Wrong-run or wrong-person owner review binding requires isolated owner-private history/journal path.",
    "E2E-50": "Owner identity assertions require a separately trusted owner authenticator; cannot be inferred from CLI fields.",
    "E2E-51": "Phoenix calendar date boundary needs a deterministic timezone clock and boundary test.",
    "E2E-52": "Missing specialist activation requires real host-native invocation evidence unavailable after turn/start rejection.",
    "E2E-53": "All 14 conditional skill activations require trustworthy real-host event evidence.",
    "E2E-54": "Seven consecutive real daily runs and forty independent reviews cannot be simulated as proof.",
}


def _claim(cid, kind, text):
    return {
        "claim_id": cid, "claim_type": kind, "claim_text": text,
        "source_url": "https://employer.example/strategy",
        "publisher": "Synthetic Employer", "source_origin_id": "synthetic-origin",
        "retrieved_at": date.today().isoformat(),
        "published_on": date.today().isoformat(), "page_read_success": True,
        "excerpt": "Synthetic page states: " + text,
        "support_relationship": "DIRECT", "subject_id": "org-synthetic",
        "object_id": None,
    }


def _packet():
    objective = _claim("objective", "BUSINESS_OBJECTIVE",
                       "Modernize enterprise platforms and improve customer operations.")
    role = _claim("role", "CURRENT_EXECUTIVE_ROLE", "Pat Example serves as product executive.")
    role.update(subject_id="person-synthetic", object_id="org-synthetic")
    ownership = _claim("ownership", "EXECUTIVE_OWNERSHIP",
                       "Pat Example sponsors the platform modernization initiative.")
    ownership.update(subject_id="person-synthetic", object_id="initiative-synthetic")
    problem = _claim("operational-problem", "OPERATIONAL_PROBLEM",
                     "AI pilots are duplicated across product teams and their adoption is not measured.")
    problem["object_id"] = "initiative-synthetic"
    trigger = _claim("trigger", "BUSINESS_TRIGGER", "The employer announced an operating model change.")
    record = {
        "schema_version": "2.2", "project_id": "PERSONAL_CAREER_OUTREACH",
        "purpose": "Explore personal senior leadership career opportunities",
        "engagement_pathway": "STRATEGIC_EXPLORATION", "capability_theme": "ENTERPRISE_PRODUCT_LEADERSHIP",
        "organization": {"organization_id": "org-synthetic", "name": "Synthetic Employer",
                         "work_mode": "TUCSON", "feasible": True},
        "initiative": {"initiative_id": "initiative-synthetic", "objective_claim_id": "objective"},
        "claims": [objective, role, ownership, problem, trigger],
        "contribution": {"business_objective_claim_id": "objective",
                         "candidate_basis": "Enterprise product strategy and product leadership experience",
                         "candidate_claim_approved": True,
                         "proposed_value": "Lead product prioritization and adoption for enterprise workflows",
                         "mandate_key": "synthetic-product-mandate", "leadership_need_assumed": False,
                         "hiring_claim": False},
        "executive": {"person_id": "person-synthetic", "name": "Pat Example",
                      "current_role_claim_id": "role", "opted_out": False,
                      "ownership": {"role_type": "BUSINESS_OUTCOME_OWNER", "ownership_grade": "DOCUMENTED",
                                    "claim_id": "ownership"},
                      "route": {"route_type": "WARM_INTRO", "url": "https://association.example/intro",
                                "verified_for_person": True}},
        "job": None,
        "career_value": {"business_decision": "Choose product investments that improve measurable operational outcomes",
                         "proposed_internal_responsibility": "Lead product portfolio prioritization and cross-functional adoption",
                         "candidate_evidence_refs": ["MOBIUS_PRODUCT_PORTFOLIO", "MOBIUS_PRODUCT_TEAM_LEADERSHIP"],
                         "complementary_scope": "Direct adoption alongside existing technical leadership",
                         "existing_owner_status": "OWNER_RESEARCHED_NOT_FOUND",
                         "expected_outcome": "Improve adoption and measurable workflow outcomes",
                         "limitations": "No demonstrated clinical or utility-specific qualifications",
                         "trigger_claim_id": "trigger", "maturity": "PILOTED",
                         "problem_claim_id": "operational-problem",
                         "outcome_metric": "Percentage of prioritized AI products adopted by teams",
                         "mandate_boundary": "COMPLEMENTARY_INTERNAL_SCOPE"},
    }
    return {"schema_version": "2.2", "project_id": "PERSONAL_CAREER_OUTREACH",
            "run_id": "synthetic-e2e-" + date.today().isoformat(),
            "date_local": date.today().isoformat(), "opportunities": [record]}


def _as_remote_direct_hire(record):
    """Turn a valid strategic fixture into a contract-valid synthetic ATS case."""
    record = deepcopy(record)
    record["engagement_pathway"] = "DIRECT_HIRING"
    record["executive"] = None
    record["organization"]["work_mode"] = "US_REMOTE"
    record["claims"] = [c for c in record["claims"] if c["claim_type"] == "BUSINESS_OBJECTIVE"]
    job_claim = _claim("job-active", "JOB_ACTIVE", "Applications are open for synthetic requisition R-100.")
    job_claim["object_id"] = "R-100"
    job_claim["source_url"] = "https://employer.example/jobs/R-100"
    record["claims"].append(job_claim)
    record["job"] = {
        "requisition_id": "R-100", "official_ats_url": "https://employer.example/jobs/R-100",
        "status_claim_id": "job-active", "state": "ACCEPTING",
        "mandatory_qualifications": [{"requirement": "Relevant experience", "status": "MATCHED",
                                       "candidate_evidence_refs": ["MOBIUS_PRODUCT_PORTFOLIO"]}],
        "work_mode_feasible": True,
        "candidate_eligibility": {"work_authorization": "ELIGIBLE"},
        "role_relevance": "MATCH", "remote_eligibility": "NOT_AZ_ELIGIBLE",
    }
    return record


def _scenario(case_id):
    p = _packet()
    x = p["opportunities"][0]
    # Each case declares whether today's CLI can observe the behavior. A HOLD
    # is an explicit coverage gap, not a successful approximation.
    if case_id == "E2E-01":
        x["claims"][0]["claim_text"] = "Modernize enterprise platforms and improve customer operations."
        x["claims"][0]["excerpt"] = "Synthetic page states: " + x["claims"][0]["claim_text"]
        x["career_value"]["business_decision"] = "Improve customer operations through platform modernization"
        return p, "CLI accepts a business objective without AI terminology and retains a bounded contribution.", "assert", lambda r: r["assessments"][0]["career_value_assessment"]["contribution_quality"] == "STRONG_CONTRIBUTION"
    if case_id == "E2E-02":
        x["claims"][0]["claim_text"] = "Transform, innovate, and lead the future with next-generation intelligence."
        x["claims"][0]["excerpt"] = "Synthetic page states: " + x["claims"][0]["claim_text"]
        x["career_value"]["business_decision"] = x["claims"][0]["claim_text"]
        x["claims"] = [c for c in x["claims"] if c["claim_id"] != "operational-problem"]
        x["career_value"]["problem_claim_id"] = None
        return p, "Buzzword-only objective must not be promoted to strong contribution.", "assert", lambda r: r["assessments"][0]["career_value_assessment"]["contribution_quality"] != "STRONG_CONTRIBUTION"
    if case_id == "E2E-03":
        x["claims"][0]["claim_text"] = "The prestigious Tucson employer is widely recognized as a local brand leader."
        x["claims"][0]["excerpt"] = "Synthetic page states: " + x["claims"][0]["claim_text"]
        x["career_value"]["business_decision"] = "Join a prestigious Tucson organization"
        x["career_value"]["expected_outcome"] = "Build a leadership career at a prestigious local brand"
        x["claims"] = [c for c in x["claims"] if c["claim_id"] != "operational-problem"]
        x["career_value"]["problem_claim_id"] = None
        x["career_value"].pop("outcome_metric")
        return p, "Local prestige without a substantive business decision/value is not strong contribution.", "assert", lambda r: r["assessments"][0]["career_value_assessment"]["contribution_quality"] != "STRONG_CONTRIBUTION"
    if case_id == "E2E-04":
        x = _as_remote_direct_hire(x)
        p["opportunities"][0] = x
        return p, "Arizona-excluded remote role is held as ineligible based on explicit remote eligibility.", "assert", lambda r: "ARIZONA_REMOTE_INELIGIBLE" in r["assessments"][0]["reasons"] and r["assessments"][0]["research_state"] == "EVIDENCE_HOLD"
    if case_id == "E2E-05":
        return p, "Transferable regulated product leadership may be supported without inventing industry credentials.", "hold", None
    if case_id == "E2E-06":
        return p, "Capability theme remains distinct from direct-hiring versus strategic pathway qualification.", "hold", None
    if case_id == "E2E-07":
        x["claims"][-1]["published_on"] = (date.today() - timedelta(days=300)).isoformat()
        x["claims"][-1]["retrieved_at"] = date.today().isoformat()
        return p, "Stale trigger yields MONITOR_TRIGGER, not RESEARCH_NOW.", "assert", lambda r: r["assessments"][0]["career_value_assessment"]["timing_status"] == "MONITOR_TRIGGER"
    if case_id == "E2E-08":
        return p, "Maturity labels must distinguish announcement, pilot, deployment, and scale evidence.", "hold", None
    if case_id == "E2E-09":
        x["contribution"]["hiring_claim"] = False
        x["career_value"]["trigger_claim_id"] = "trigger"
        x["claims"][-1]["claim_text"] = "A new chief product officer was appointed this quarter."
        x["claims"][-1]["excerpt"] = "Synthetic page states: " + x["claims"][-1]["claim_text"]
        return p, "Business trigger does not prove staffing need, hiring, or a vacancy.", "assert", lambda r: r["assessments"][0]["career_value_assessment"]["leadership_gap_or_hiring_proven"] is False and r["contact_ready"] == 0
    if case_id == "E2E-10":
        x["career_value"]["existing_owner_status"] = "EXISTING_OWNER_DOCUMENTED"
        return p, "Existing product ownership requires comparative review and cannot be silently treated as a gap.", "assert", lambda r: "EXISTING_OWNER_REMIT_REQUIRES_COMPARATIVE_REVIEW" in r["assessments"][0]["career_value_assessment"]["reason_codes"]
    if case_id == "E2E-11":
        x["claims"][0]["claim_text"] = "The organization is excited about AI and innovation."
        x["claims"][0]["excerpt"] = "Synthetic page states: " + x["claims"][0]["claim_text"]
        x["career_value"]["business_decision"] = "Provide generic AI strategy leadership"
        x["career_value"]["expected_outcome"] = "Advance AI strategy and innovation"
        x["claims"] = [c for c in x["claims"] if c["claim_id"] != "operational-problem"]
        x["career_value"]["problem_claim_id"] = None
        x["career_value"].pop("outcome_metric")
        x["career_value"]["mandate_boundary"] = "REQUIRES_SCOPE_REVIEW"
        return p, "Generic strategy pitch without a bounded business outcome must not qualify as strong contribution.", "assert", lambda r: r["assessments"][0]["career_value_assessment"]["contribution_quality"] != "STRONG_CONTRIBUTION"
    if case_id == "E2E-12":
        return p, "Bounded product adoption value is retained only as an unverified hypothesis, with no contact authority.", "assert", lambda r: r["assessments"][0]["career_value_assessment"]["contribution_quality"] == "STRONG_CONTRIBUTION" and r["source_truth_independently_verified"] is False and r["contact_ready"] == 0 and r["send_authorized"] is False
    if case_id == "E2E-13":
        x["career_value"]["candidate_evidence_refs"] = ["UNSUBSTANTIATED_SKILL"]
        return p, "Unsupported candidate skill reference is rejected by the packet preflight.", "reject", None
    if case_id == "E2E-14":
        x["career_value"]["candidate_evidence_refs"] = ["CLINICAL_CREDENTIAL_NOT_IN_PROFILE"]
        x["career_value"]["limitations"] = "Clinical credential claimed without approved evidence"
        return p, "Unsubstantiated clinical or utility credential is rejected by the packet preflight.", "reject", None
    if case_id == "E2E-15":
        x["career_value"]["proposed_internal_responsibility"] = "Perform hands-on model engineering and production coding"
        return p, "Hands-on engineering role outside leadership scope is excluded or held.", "hold", None
    if case_id == "E2E-16":
        x["career_value"]["existing_owner_status"] = "EXISTING_OWNER_DOCUMENTED"
        x["career_value"]["proposed_internal_responsibility"] = "Replace the established chief product officer and own the whole chief function"
        x["career_value"]["complementary_scope"] = "Take over the existing chief function"
        x["career_value"]["mandate_boundary"] = "REPLACES_EXISTING_CHIEF_FUNCTION"
        return p, "Candidate cannot claim to replace an established chief function; evaluator should hold or bound the contribution.", "assert", lambda r: r["assessments"][0]["career_value_assessment"]["contribution_quality"] != "STRONG_CONTRIBUTION"
    # E2E-17..51: source, continuity and governance synthetic probes.
    # A case receives PASS only for a property observed through the bounded CLI.
    # Unobservable source semantics, private memory, native host and multi-run
    # properties remain HOLD; a generic no-send assertion is not substituted.
    if case_id == "E2E-17":
        x["claims"][0]["page_read_success"] = False
        return p, "Unavailable objective source cannot establish assessable source evidence.", "assert", lambda r: (
            r["assessments"][0]["research_state"] == "EVIDENCE_HOLD"
            and r["source_truth_independently_verified"] is False)
    if case_id == "E2E-18":
        x["claims"][0]["page_read_success"] = True  # intentionally untrusted caller flag
        return p, "Caller-asserted page read cannot be independent source verification.", "assert", lambda r: (
            r["source_truth_independently_verified"] is False
            and r["stage_manifest"]["source_provenance"] == "SELF_REPORTED_NOT_INDEPENDENTLY_VERIFIED")
    if case_id == "E2E-24":
        x["executive"]["ownership"]["ownership_grade"] = "FUNCTIONALLY_PLAUSIBLE"
        return p, "Executive title without documented initiative ownership stays unverified.", "assert", lambda r: (
            "EXECUTIVE_OWNER_UNVERIFIED" in r["assessments"][0]["reasons"]
            and r["contact_ready"] == 0)
    if case_id == "E2E-25":
        x["claims"][2]["object_id"] = "other-unrelated-initiative"
        return p, "General executive AI remit is not direct evidence of this initiative ownership.", "assert", lambda r: (
            "EXECUTIVE_OWNERSHIP_SOURCE_MISSING" in r["assessments"][0]["reasons"]
            and r["contact_ready"] == 0)
    if case_id == "E2E-28":
        first = _as_remote_direct_hire(x)
        first["job"]["remote_eligibility"] = "AZ_ELIGIBLE"
        second = deepcopy(first)
        second["job"]["requisition_id"] = "R-101"
        second["job"]["official_ats_url"] = "https://employer.example/jobs/R-101"
        second["job"]["status_claim_id"] = "job-active-101"
        for c in second["claims"]:
            if c["claim_id"] == "job-active":
                c["claim_id"] = "job-active-101"
                c["object_id"] = "R-101"
                c["source_url"] = "https://employer.example/jobs/R-101"
                c["claim_text"] = "Applications are open for synthetic requisition R-101."
                c["excerpt"] = "Synthetic page states: " + c["claim_text"]
        p["opportunities"] = [first, second]
        return p, "Two distinct ATS requisitions at one employer retain distinct identities.", "assert", lambda r: (
            r["reviewed"] == 2 and
            len({tuple(a["opportunity_identity"]) for a in r["assessments"]}) == 2 and
            all("IDENTITY_COLLISION_HOLD" not in a["reasons"] for a in r["assessments"]))
    if case_id == "E2E-32":
        second = deepcopy(x)
        second["contribution"]["mandate_key"] = "separate-product-adoption-mandate"
        p["opportunities"] = [x, second]
        return p, "Distinct mandates under one initiative stay separately identifiable.", "assert", lambda r: (
            r["reviewed"] == 2 and
            len({tuple(a["opportunity_identity"]) for a in r["assessments"]}) == 2 and
            all("IDENTITY_COLLISION_HOLD" not in a["reasons"] for a in r["assessments"]))
    if case_id == "E2E-33":
        return p, "A strategic exploration without an official posted role never becomes posted hiring.", "assert", lambda r: (
            r["assessments"][0]["hiring_evidence"] == "STRATEGIC_ACTIVITY_NO_HIRING_EVIDENCE"
            and r["applications_submitted"] == 0)
    if case_id == "E2E-39":
        x["executive"]["route"]["verified_for_person"] = False
        x["executive"]["route"]["route_type"] = "MANUAL"
        return p, "A public profile does not attest to a working person-specific messaging route.", "assert", lambda r: (
            "NO_VERIFIED_PERSON_ROUTE" in r["assessments"][0]["reasons"] and r["contact_ready"] == 0)
    if case_id == "E2E-40":
        x["executive"]["route"]["route_type"] = "INDIRECT_GENERAL"
        x["executive"]["route"]["verified_for_person"] = False
        x["executive"]["route"]["url"] = "https://employer.example/press"
        return p, "General press inbox cannot be promoted to a person-specific route.", "assert", lambda r: (
            "NO_VERIFIED_PERSON_ROUTE" in r["assessments"][0]["reasons"] and r["contact_ready"] == 0)
    if case_id == "E2E-43":
        x["executive"]["opted_out"] = True
        return p, "Person-specific opt-out suppresses engagement, without authorizing outreach.", "assert", lambda r: (
            r["assessments"][0]["engagement_readiness"] == "SUPPRESSED"
            and "OPT_OUT_SUPPRESSION" in r["assessments"][0]["reasons"]
            and r["contact_ready"] == 0)
    if case_id == "E2E-44":
        x["purpose"] = "Send Nova Compute subcontracting proposals to government prime contractors"
        return p, "Commercial subcontracting purpose is excluded from personal career research.", "assert", lambda r: (
            r["assessments"][0]["research_state"] == "EXCLUDED"
            and r["contact_ready"] == 0 and r["send_authorized"] is False)
    if case_id == "E2E-47":
        x = _as_remote_direct_hire(x)
        x["job"]["remote_eligibility"] = "AZ_ELIGIBLE"
        p["opportunities"][0] = x
        return p, "Even structurally active ATS listing cannot submit an application.", "assert", lambda r: (
            r["assessments"][0]["hiring_evidence"] == "ACTIVE_POSTED_ROLE"
            and r["applications_submitted"] == 0
            and r["assessments"][0]["application_submitted"] is False)
    if 17 <= int(case_id.split("-")[1]) <= 54:
        return p, "Requires a distinct independent evidence oracle, private/host boundary, or multi-run workflow.", "hold", None
    raise KeyError(case_id)


def _run_cli(packet, out_dir):
    input_path = out_dir / "input.json"
    output_path = out_dir / "output.json"
    input_path.write_text(json.dumps(packet, sort_keys=True, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    proc = subprocess.run([sys.executable, str(CLI), "--input", str(input_path), "--out", str(output_path)],
                          cwd=ROOT, env=env, capture_output=True, text=True, timeout=45)
    report = json.loads(output_path.read_text(encoding="utf-8")) if output_path.exists() else None
    return input_path, output_path, proc, report


def run_cases(result_path: Path, case_ids: list[str] | None = None):
    inventory = json.loads(MATRIX.read_text(encoding="utf-8"))
    selected = case_ids or [f"E2E-{i:02}" for i in range(1, 17)]
    expected_ids = {c["id"] for c in inventory["cases"]}
    if not set(selected) <= expected_ids:
        raise ValueError("CASE_ID_NOT_IN_STATIC_INVENTORY")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    stamp = datetime.now(timezone.utc).isoformat()
    result_path = result_path.expanduser().resolve()
    if result_path == ROOT or ROOT in result_path.parents:
        raise ValueError("RESULT_REGISTER_MUST_BE_OUTSIDE_REPOSITORY")
    result_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_root = result_path.parent / (result_path.stem + "-evidence-" + uuid.uuid4().hex)
    artifact_root.mkdir(parents=True, exist_ok=True)
    entries = []
    for cid in selected:
        case = next(c for c in inventory["cases"] if c["id"] == cid)
        packet, expected, mode, assertion = _scenario(cid)
        case_dir = artifact_root / cid
        case_dir.mkdir(parents=True, exist_ok=True)
        input_path, output_path, proc, report = _run_cli(packet, case_dir)
        digest = hashlib.sha256(input_path.read_bytes()).hexdigest()
        observed = {
            "returncode": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
            "cli_status": report.get("status") if report else None,
            "research_state": report["assessments"][0].get("research_state") if report else None,
            "contribution_quality": report["assessments"][0].get("career_value_assessment", {}).get("contribution_quality") if report else None,
            "timing_status": report["assessments"][0].get("career_value_assessment", {}).get("timing_status") if report else None,
            "reason_codes": report["assessments"][0].get("career_value_assessment", {}).get("reason_codes", []) if report else [],
            "source_truth_independently_verified": report.get("source_truth_independently_verified") if report else None,
            "native_skills_verified": report.get("native_skills_verified") if report else None,
            "contact_ready": report.get("contact_ready") if report else None,
            "send_authorized": report.get("send_authorized") if report else None,
        }
        if mode == "hold":
            status = "HOLD"
            observation = HOLD_BLOCKERS.get(cid, "No trusted executable oracle in this synthetic CLI for this case; requires independently observed workflow evidence.")
        elif mode == "reject":
            passed = proc.returncode != 0 and report is None and "V2.2_SCHEMA_INVALID" in proc.stderr
            status = "PASS" if passed else "FAIL"
            observation = "Preflight rejected unsupported candidate evidence." if passed else "Expected schema rejection was not observed."
        else:
            try:
                passed = proc.returncode == 0 and report is not None and bool(assertion(report))
            except Exception:
                passed = False
            status = "PASS" if passed else "FAIL"
            observation = "Expected observable assertion matched CLI output." if passed else "Expected observable assertion did not match CLI output."
        entries.append({
            "case_id": cid, "case_name": case["name"], "commit_sha": commit,
            "input_digest_sha256": digest, "run_timestamp_utc": stamp,
            "expected_behavior": expected, "actual_observation": {**observed, "assertion": observation},
            "evidence_reference": {"input": str(input_path), "cli_output": str(output_path),
                                   "stdout_stderr_in_register": True},
            "assurance_level": "SYNTHETIC_CLI" if mode != "hold" else "SYNTHETIC_CLI_LIMITED_ASSERTION",
            "status": status, "live_host_qualified": False,
            "source_truth_independently_verified": False,
        })
    result = {"schema_version": "1.0", "inventory_path": "evals/career_v22_e2e_matrix.json",
              "inventory_unchanged": True,
              "branch": subprocess.run(["git", "branch", "--show-current"], cwd=ROOT, capture_output=True,
                                       text=True, check=True).stdout.strip(),
              "evidence_directory": str(artifact_root),
              "commit_sha": commit, "run_timestamp_utc": stamp,
              "harness_digest_sha256": hashlib.sha256(b"".join(p.read_bytes() for p in HARNESS_FILES if p.exists())).hexdigest(),
              "assurance_notice": "Synthetic CLI execution only; never LIVE_HOST_QUALIFIED or production qualification.",
              "case_results": entries}
    temp = result_path.with_suffix(result_path.suffix + ".tmp")
    temp.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(temp, result_path)
    counts = {s: sum(e["status"] == s for e in entries) for s in ("PASS", "FAIL", "HOLD", "NOT_RUN")}
    print(json.dumps({"register": str(result_path), "evidence_dir": str(artifact_root), "counts": counts}, indent=2))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", required=True, help="JSON register path outside public repository")
    parser.add_argument("--cases", nargs="*", help="case IDs; defaults to E2E-01 through E2E-16")
    args = parser.parse_args()
    run_cases(Path(args.results), args.cases)


if __name__ == "__main__":
    main()