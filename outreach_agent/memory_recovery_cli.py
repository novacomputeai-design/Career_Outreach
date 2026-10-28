"""Manual owner-only memory backup CLI. Never a Codex sandbox or network endpoint."""
import argparse
import json
import os
from .memory_recovery import create_encrypted_backup, verify_encrypted_backup, restore_to_new_file
from .state import PrivateStore

def main(argv=None):
    p = argparse.ArgumentParser(description="Protected owner-only memory backup and recovery; no sending")
    sub = p.add_subparsers(dest="action", required=True)
    backup = sub.add_parser("backup")
    backup.add_argument("--db", required=True)
    backup.add_argument("--out", required=True)
    verify = sub.add_parser("verify")
    verify.add_argument("--snapshot", required=True)
    recover = sub.add_parser("restore-new")
    recover.add_argument("--snapshot", required=True)
    recover.add_argument("--destination", required=True)
    args = p.parse_args(argv)
    state_key = os.getenv("OUTREACH_STATE_KEY")
    identity_key = os.getenv("OUTREACH_IDENTITY_KEY")
    if not state_key or not identity_key:
        p.error("Owner's original state and identity keys are required")
    if args.action == "backup":
        store = PrivateStore(args.db, key=state_key, identity_key=identity_key, read_only=True)
        try:
            result = create_encrypted_backup(store, args.out)
        finally:
            store.close()
    elif args.action == "verify":
        result = verify_encrypted_backup(args.snapshot, state_key, identity_key)
    else:
        result = restore_to_new_file(args.snapshot, args.destination, state_key, identity_key)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
