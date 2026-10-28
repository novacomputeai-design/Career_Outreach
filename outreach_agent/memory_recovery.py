"""Owner-only encrypted SQLite backup, verification, and new-path recovery.

No network, no Codex sandbox access, no key export, and never overwrite live DB.
Consistent SQLite snapshots are serialized in memory before Fernet encryption.
A valid snapshot requires BOTH the original Fernet state key and HMAC identity key.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import sqlite3
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

from .state import REPO, PrivateStore

MAGIC = b"CAREER-OUTREACH-ENCRYPTED-SQLITE-V1\n"
IDENTITY_CONTEXT = b"CareerOutreach:memory-recovery:identity-key:v1"
MAX_BACKUP_BYTES = 256 * 1024 * 1024
REQUIRED_TABLES = frozenset({
    "people", "events", "approvals", "preferences", "recommendations",
    "runs", "governance_decisions",
})


def _private_path(path: str | Path) -> Path:
    result = Path(path).expanduser().resolve()
    if result == REPO or REPO in result.parents:
        raise ValueError("Backups and restored databases must stay outside Git checkout")
    return result


def _keys(state_key: bytes | str, identity_key: bytes | str):
    state = state_key.encode() if isinstance(state_key, str) else state_key
    identity = identity_key.encode() if isinstance(identity_key, str) else identity_key
    if not state or not identity or len(identity) < 32:
        raise RuntimeError("Original state and identity keys are required")
    return Fernet(state), identity


def _check_database(db: sqlite3.Connection) -> None:
    integrity = db.execute("PRAGMA integrity_check").fetchone()
    if not integrity or integrity[0] != "ok":
        raise ValueError("Snapshot SQLite integrity verification failed")
    available = {row[0] for row in db.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}
    if not REQUIRED_TABLES.issubset(available):
        raise ValueError("Snapshot does not have the required private-memory tables")


def _tag(identity_key: bytes) -> bytes:
    return hmac.new(identity_key, IDENTITY_CONTEXT, hashlib.sha256).digest()


def create_encrypted_backup(store: PrivateStore, target: str | Path) -> dict:
    """Backup live read-only SQLite using online snapshot; no plaintext disk copy."""
    if not store.read_only:
        raise ValueError("Snapshot source must be opened in SQLite read-only mode")
    dest = _private_path(target)
    if dest.exists():
        raise FileExistsError("Backup already exists; never overwrite it")
    mem = sqlite3.connect(":memory:")
    try:
        store.db.backup(mem)
        _check_database(mem)
        raw = mem.serialize()
    finally:
        mem.close()
    # A SQLite online backup from WAL mode can retain WAL-mode header bytes.
    # The serialized snapshot already contains committed pages, so use the
    # ordinary rollback-mode header before in-memory deserialize/verify.
    if raw[18:20] == bytes((2, 2)):
        raw = raw[:18] + bytes((1, 1)) + raw[20:]
    if raw[18:20] != bytes((1, 1)):
        raise ValueError('Unsupported SQLite snapshot journal header')
    check = sqlite3.connect(':memory:')
    try:
        check.deserialize(raw)
        _check_database(check)
    finally:
        check.close()
    if len(raw) > MAX_BACKUP_BYTES // 2:
        raise ValueError("Snapshot exceeds safe in-memory backup size")
    encrypted = MAGIC + store.crypt.encrypt(_tag(store.identity_key) + raw)
    dest.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        with dest.open("xb") as output:
            if os.name == "posix":
                os.chmod(dest, 0o600)
            output.write(encrypted)
    except Exception:
        # Do not leave a partial backup that could be mistaken for a valid one.
        if dest.exists():
            dest.unlink()
        raise
    return {"status": "ENCRYPTED_SNAPSHOT_CREATED",
            "contains_plaintext_credentials": False,
            "source_database_modified": False,
            "requires_original_state_and_identity_keys": True}


def _authenticated_snapshot(snapshot: str | Path, state_key, identity_key) -> sqlite3.Connection:
    fernet, identity = _keys(state_key, identity_key)
    target = _private_path(snapshot)
    if not target.is_file():
        raise FileNotFoundError("Encrypted snapshot not found")
    if target.stat().st_size > MAX_BACKUP_BYTES:
        raise ValueError("Encrypted snapshot exceeds configured limit")
    data = target.read_bytes()
    if not data.startswith(MAGIC):
        raise ValueError("Unknown or unencrypted backup format")
    try:
        plaintext = fernet.decrypt(data[len(MAGIC):])
    except InvalidToken as exc:
        raise ValueError("Backup decryption/authentication failed; keys may differ") from exc
    tag_bytes, raw = plaintext[:32], plaintext[32:]
    if not hmac.compare_digest(tag_bytes, _tag(identity)):
        raise ValueError("Identity key does not match this encrypted backup")
    mem = sqlite3.connect(":memory:")
    try:
        mem.deserialize(raw)
        _check_database(mem)
        # At least one contact's private encrypted payload must be readable.
        row = mem.execute("SELECT encrypted_record FROM people LIMIT 1").fetchone()
        if row:
            try:
                fernet.decrypt(row[0])
            except InvalidToken as exc:
                raise ValueError("Private record encryption key mismatch") from exc
    except Exception:
        mem.close()
        raise
    return mem


def verify_encrypted_backup(snapshot, state_key, identity_key) -> dict:
    mem = _authenticated_snapshot(snapshot, state_key, identity_key)
    mem.close()
    return {"status": "AUTHENTICATED_SQLITE_BACKUP_VALID",
            "original_keys_match": True,
            "private_records_printed": False,
            "live_database_modified": False}


def restore_to_new_file(snapshot, destination, state_key, identity_key) -> dict:
    """Restore verified snapshot only to a NEW path; never replace live database."""
    dest = _private_path(destination)
    if dest.exists():
        raise FileExistsError("Recovery destination exists; live files cannot be overwritten")
    mem = _authenticated_snapshot(snapshot, state_key, identity_key)
    created = False
    try:
        dest.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        # Refuse overwrite even if a file appears between the existence check and open.
        with dest.open("xb"):
            created = True
        if os.name == "posix":
            os.chmod(dest, 0o600)
        restored = sqlite3.connect(str(dest))
        try:
            mem.backup(restored)
            _check_database(restored)
        finally:
            restored.close()
    except Exception:
        if created:
            dest.unlink(missing_ok=True)
        raise
    finally:
        mem.close()
    return {"status": "RESTORED_TO_NEW_PRIVATE_PATH",
            "live_database_overwritten": False,
            "requires_original_state_and_identity_keys": True}
