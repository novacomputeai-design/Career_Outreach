#!/usr/bin/env python3
"""Pure-stdlib structural validator; does not prove autonomous skill execution."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"
EXPECTED = {
    "daily-executive-outreach", "organization-discovery", "leadership-discovery",
    "contact-verification", "relationship-qualification", "relationship-memory",
    "outreach-drafting", "daily-executive-brief", "run-quality-audit",
    "follow-up-planning", "conversation-preparation"
}

def validate():
    errors = []
    found = {p.name for p in SKILLS.iterdir() if p.is_dir()} if SKILLS.exists() else set()
    for name in sorted(EXPECTED - found):
        errors.append("missing skill: " + name)
    for name in sorted(found):
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
            errors.append("bad skill directory: " + name)
        source = SKILLS / name / "SKILL.md"
        if not source.is_file():
            errors.append("missing SKILL.md: " + name)
            continue
        text = source.read_text(encoding="utf-8")
        match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, flags=re.S)
        if not match:
            errors.append("bad YAML frontmatter: " + name)
            continue
        metadata = match.group(1)
        names = re.findall(r"^name:\s*(.+)$",metadata,re.M)
        descriptions = re.findall(r"^description:\s*(.+)$",metadata,re.M)
        if names != [name]:
            errors.append("mismatched skill name: " + name)
        if len(descriptions) != 1 or not 1 <= len(descriptions[0]) <= 1024:
            errors.append("invalid skill description: " + name)
        elif ": " in descriptions[0] and not descriptions[0].startswith(("\\\"", "\u0027")):
            errors.append("unquoted YAML colon in skill description: " + name)
    for path in ("config/operating-policy.json","evals/cases.json"):
        try:
            json.loads((ROOT/path).read_text(encoding="utf-8"))
        except (OSError,ValueError) as e:
            errors.append("bad JSON " + path + ": " + str(e))
    for path in ("AGENTS.md","references/daily-operating-contract.md",
                 "references/scoring-rubric.md","references/source-and-contact-policy.md",
                 "config/public-candidate-profile.md"):
        if not (ROOT/path).is_file():
            errors.append("missing reference: "+path)
    return errors

if __name__ == "__main__":
    issues=validate()
    if issues:
        print("\n".join("FAIL: "+x for x in issues))
        raise SystemExit(1)
    print("PASS: 11 skill definitions and project JSON/reference structure (structural only)")
