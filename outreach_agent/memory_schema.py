"""Explicit owner-only migration of original private memory to audited schema.

Never modifies existing relationship rows, has no network or sending.
Before any schema write, creates and independently verifies an authenticated
encrypted backup using the existing DPAPI-unlocked owner keys.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .memory_recovery import (
    _private_path, _check_database, SCHEMA_LEGACY, SCHEMA_CURRENT,
    create_encrypted_backup, verify_encrypted_backup,
)
from .state import PrivateStore

BASE = ("people", "events", "approvals", "preferences", "recommendations", "runs")

def _connect_existing(db_path: str | Path, *, write: bool = False) -> sqlite3.Connection:
    source = _private_path(db_path)
    if not source.is_file():
        raise FileNotFoundError("Existing private relationship database required")
    if write:
        db = sqlite3.connect(str(source), timeout=10)
    else:
        db = sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)
    return db

def inspect_memory_schema(db_path: str | Path) -> dict:
    db = _connect_existing(db_path)
    try:
        version = _check_database(db)
        counts = {name: int(db.execute(
            'SELECT COUNT(*) FROM "' + name + '"').fetchone()[0]) for name in BASE}
    finally:
        db.close()
    return {"status": "PRIVATE_SCHEMA_INSPECTED",
            "schema_variant": version,
            "existing_record_counts": counts,
            "database_modified": False,
            "send_authorized": False}

def migrate_governance_schema(db_path: str | Path, backups_dir: str | Path,
                              state_key: bytes | str, identity_key: bytes | str) -> dict:
    """Explicit operator action: backup+verify first; create audit table only."""
    source = _private_path(db_path)
    out_dir = _private_path(backups_dir)
    if source == out_dir or out_dir == source.parent and source.name.endswith(".fernet"):
        raise ValueError("Expected an existing SQLite file, not an encrypted snapshot")
    baseline = inspect_memory_schema(source)
    if baseline["schema_variant"] == SCHEMA_CURRENT:
        return {"status": "ALREADY_CURRENT_NO_CHANGES",
                "schema_variant": SCHEMA_CURRENT, "database_modified": False}
    if baseline["schema_variant"] != SCHEMA_LEGACY:
        raise ValueError("Unrecognized schema; migration not authorized")

    name = ("schema-before-governance-" +
            datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S") +
            "-" + uuid.uuid4().hex[:12] + ".fernet")
    backup_path = out_dir / name
    store = PrivateStore(source, key=state_key, identity_key=identity_key,
                         read_only=True)
    try:
        created = create_encrypted_backup(store, backup_path)
    finally:
        store.close()
    if created["schema_variant"] != SCHEMA_LEGACY:
        raise ValueError("Backup unexpectedly changed schema; live database untouched")
    verified = verify_encrypted_backup(backup_path, state_key, identity_key)
    if verified["schema_variant"] != SCHEMA_LEGACY:
        raise ValueError("Verified backup does not match legacy schema")

    # The backup exists and both original keys have been checked.
    # Only now is a single additive SQLite DDL statement authorized.
    writer = _connect_existing(source, write=True)
    try:
        writer.execute("BEGIN IMMEDIATE")
        if _check_database(writer) != SCHEMA_LEGACY:
            raise ValueError("Database changed after backup; migration held")
        current_counts = {table: int(writer.execute(
            'SELECT COUNT(*) FROM "' + table + '"').fetchone()[0]) for table in BASE}
        if current_counts != baseline["existing_record_counts"]:
            raise ValueError("Database changed since preflight; migration held")
        writer.execute("""
            CREATE TABLE governance_decisions (
                audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id TEXT NOT NULL,
                action TEXT NOT NULL,
                policy_version TEXT NOT NULL,
                verdict TEXT NOT NULL,
                occurred_at TEXT NOT NULL,
                encrypted_detail BLOB NOT NULL
            )
        """)
        if _check_database(writer) != SCHEMA_CURRENT:
            raise ValueError("Post-migration schema validation failed")
        end_counts = {table: int(writer.execute(
            'SELECT COUNT(*) FROM "' + table + '"').fetchone()[0]) for table in BASE}
        if current_counts != end_counts:
            raise ValueError("Unexpected change in existing relationship row counts")
        from cryptography.fernet import Fernet
        key = state_key.encode() if isinstance(state_key, str) else state_key
        digest = hashlib.sha256(backup_path.read_bytes()).hexdigest()
        audit = Fernet(key).encrypt(json.dumps({
            "event": "OWNER_APPROVED_ADDITIVE_SCHEMA_MIGRATION",
            "previous_schema": SCHEMA_LEGACY,
            "backup_ciphertext_sha256": digest,
            "prior_existing_row_counts": current_counts,
        }).encode("utf-8"))
        writer.execute("""
            INSERT INTO governance_decisions
            (person_id,action,policy_version,verdict,occurred_at,encrypted_detail)
            VALUES(?,?,?,?,?,?)
        """, ("__SYSTEM__", "SCHEMA_MIGRATION", "0.2.1",
              "OWNER_INITIATED_APPLIED", datetime.now(timezone.utc).isoformat(), audit))
        writer.commit()
    except Exception:
        writer.rollback()
        raise
    finally:
        writer.close()
    after = inspect_memory_schema(source)
    if after["schema_variant"] != SCHEMA_CURRENT:
        raise RuntimeError("Schema migration post-verification failed; retain preflight backup")
    return {"status": "GOVERNANCE_AUDIT_SCHEMA_ADDED",
            "schema_variant": SCHEMA_CURRENT,
            "backup_verified_before_change": True,
            "backup_file": str(backup_path),
            "original_relationship_row_counts_unchanged":
                after["existing_record_counts"] == baseline["existing_record_counts"],
            "existing_relationship_history_preserved": True,
            "no_messages_sent": True}
