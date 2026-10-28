"""Owner-only read/explicit-migrate CLI, never a Codex or network entrypoint."""
from __future__ import annotations

import argparse
import json
import os

from .memory_schema import inspect_memory_schema, migrate_governance_schema

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Inspect or explicitly migrate private memory audit schema")
    sub = parser.add_subparsers(dest="action", required=True)
    inspect = sub.add_parser("inspect")
    inspect.add_argument("--db", required=True)
    migrate = sub.add_parser("migrate")
    migrate.add_argument("--db", required=True)
    migrate.add_argument("--backups-dir", required=True)
    migrate.add_argument("--operator-approved", action="store_true", required=True)
    args = parser.parse_args(argv)
    if args.action == "inspect":
        report = inspect_memory_schema(args.db)
    else:
        state = os.getenv("OUTREACH_STATE_KEY")
        identity = os.getenv("OUTREACH_IDENTITY_KEY")
        if not state or not identity:
            parser.error("Original owner state and identity keys required")
        if args.operator_approved is not True:
            parser.error("Explicit owner approval required")
        report = migrate_governance_schema(args.db, args.backups_dir, state, identity)
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
