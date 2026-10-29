"""Static governance contract checks. NOT a live approval or source-evidence audit."""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def validate_governance(root: Path = ROOT) -> list[str]:
    issues = []
    def read(rel: str) -> str:
        try:
            return (root / rel).read_text(encoding="utf-8")
        except OSError:
            issues.append("missing governance reference: " + rel)
            return ""

    raw = read("config/operating-policy.json")
    try:
        p = json.loads(raw)
    except ValueError:
        return issues + ["invalid operating policy JSON"]
    if not isinstance(p, dict):
        return issues + ["operating policy must be an object"]
    version = str(p.get("version", ""))
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        issues.append("policy must have semantic version")
    project = p.get("project", {})
    if (project.get("id") != "PERSONAL_CAREER_OUTREACH" or
            project.get("mission") != "individual_professional_career_networking" or
            project.get("commercial_sales_outreach_prohibited") is not True or
            project.get("project_scope_failure") != "HOLD"):
        issues.append("project must remain personal career outreach, not business capture")
    if p.get("daily_target_new_people") != 20:
        issues.append("daily research target drift")
    if p.get("minimum_qualification_score") != 70:
        issues.append("minimum score drift")
    if p.get("timezone") != "America/Phoenix":
        issues.append("timezone drift")
    if p.get("outreach", {}).get("automatic_sending") is not False:
        issues.append("automatic sending must remain forbidden")
    if p.get("outreach", {}).get("individual_draft_approval") is not True:
        issues.append("per-draft human approval missing")
    if p.get("outreach", {}).get("separate_send_authorization") is not True:
        issues.append("separate send authorization missing")

    g = p.get("governance")
    if not isinstance(g, dict):
        issues.append("no versioned governance settings")
    else:
        required_truthy = (
            "contact_ready_requires_independent_human_review",
            "no_model_self_approval",
            "automatic_sending_prohibited",
            "separate_draft_and_send_authorization",
            "draft_authorization_bound_to_content_hash",
            "send_authorization_requires_qualified_identity_route_novelty",
            "codex_direct_dpapi_access_prohibited",
            "private_memory_required_for_confirmed_new",
        )
        for k in required_truthy:
            if g.get(k) is not True:
                issues.append("governance requirement disabled: " + k)
        if g.get("send_authorization_gate_status") != "BLOCKED_PENDING_RECIPIENT_ROUTE_HISTORY_PROOF":
            issues.append("send authorization policy must remain blocked until implementation")
        if g.get("history_unavailable") != "HOLD_UNVERIFIED":
            issues.append("missing private history must HOLD_UNVERIFIED")
        if g.get("existing_relationship") != "FOLLOW_UP_NOT_NEW":
            issues.append("existing relationships must not count as new")

    opp = p.get("opportunity_search", {})
    if (opp.get("version") != "1.1"
            or opp.get("mission") != "permanent_internal_leadership_employment"
            or opp.get("track_allocation") != {"AI_STRATEGY": 60, "PRODUCT_LEADERSHIP": 40}
            or opp.get("minimum_organization_score") != 75
            or opp.get("minimum_decision_maker_score") != 70
            or opp.get("organization_first") is not True
            or opp.get("never_infer_hiring_from_ai_initiative") is not True
            or opp.get("owner_attestation_requires_private_review") is not True
            or opp.get("require_person_specific_route") is not True
            or opp.get("score_never_overrides_hard_gates") is not True
            or opp.get("opportunity_assessment_contact_ready") is not False
            or opp.get("unchanged_person_drive_exporter") is not True):
        issues.append("V1.1 opportunity-first policy or safety gates drift")
    if not (root / "references/opportunity-first-contract.md").is_file():
        issues.append("V1.1 opportunity contract missing")

    m = p.get("memory")
    if not isinstance(m, dict):
        issues.append("memory authority missing")
    else:
        if set(m.get("classifications", [])) != {"FIRST_LEARNED", "PREVIOUSLY_MET"}:
            issues.append("memory relationship classifications drift")
        if m.get("private_data_in_repository") is not False:
            issues.append("private data in repository must be prohibited")
        if m.get("codex_access") != "operator_supplied_minimal_classification_until_broker_qualified":
            issues.append("Codex memory access policy drift")
    gates = p.get("production_release_gates", [])
    required = {
        "trusted_private_memory_batch_reconciliation",
        "deterministic_approval_and_contact_ready_gates",
        "private_audit_history_and_backup_recovery",
        "one_supervised_end_to_end_daily_run",
        "seven_consecutive_real_daily_runs",
        "forty_independently_reviewed_real_people",
        "no_unauthorized_outreach",
    }
    if not isinstance(gates, list) or not required.issubset(set(gates)):
        issues.append("missing mandatory production-release gates")

    plan = read("docs/PRODUCTION_PLAN.md")
    readme = read("README.md")
    agent = read("AGENTS.md")
    private_contract = read("references/private-memory-contract.md")
    memory_skill = read(".agents/skills/relationship-memory/SKILL.md")
    runbook = read("docs/OPERATING_RUNBOOK.md")
    if "P0" not in plan or "P1" not in plan or "P2" not in plan or "P3" not in plan or "P4" not in plan or "P5" not in plan:
        issues.append("production plan missing lifecycle stages")
    for path, doc in (
        ("README.md", readme),
        ("AGENTS.md", agent),
        ("references/private-memory-contract.md", private_contract),
        ("docs/OPERATING_RUNBOOK.md", runbook),
    ):
        if "config/operating-policy.json" not in doc:
            issues.append(path + " must reference authoritative policy")
    if "docs/PRODUCTION_PLAN.md" not in readme or "docs/PRODUCTION_PLAN.md" not in agent:
        issues.append("production plan must be cited by README and AGENTS")
    if "Codex may call" in private_contract or "Codex may execute" in private_contract:
        issues.append("private-memory contract permits direct Codex DPAPI lookup")
    if "not by Codex" not in private_contract:
        issues.append("private-memory contract lacks operator-only boundary")
    if "Do not invoke this wrapper from Codex" not in memory_skill:
        issues.append("memory skill lacks Codex sandbox DPAPI prohibition")
    priorities = [plan.find(f"**P{n}**") for n in range(6)]
    if any(i < 0 for i in priorities) or priorities != sorted(priorities):
        issues.append("production plan must explicitly sequence P0 through P5")
    return issues

if __name__ == "__main__":
    problems = validate_governance()
    for issue in problems:
        print("FAIL: " + issue)
    if problems:
        raise SystemExit(1)
    print("PASS: versioned memory/governance plan and critical instruction consistency (structural only)")
