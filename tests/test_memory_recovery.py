"""Synthetic owner-only SQLite recovery tests; no real data or Windows DPAPI secrets."""
import tempfile
import unittest
import sqlite3
from pathlib import Path
from cryptography.fernet import Fernet

from outreach_agent.memory_recovery import (
    create_encrypted_backup, verify_encrypted_backup, restore_to_new_file,
    SCHEMA_LEGACY, SCHEMA_CURRENT)
from outreach_agent.state import PrivateStore, REPO

class MemoryRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.path = self.root / "relationships.sqlite"
        self.state_key = Fernet.generate_key()
        self.identity = "q" * 64
        writer = PrivateStore(self.path, key=self.state_key, identity_key=self.identity)
        writer.remember_relationship("Jordan Example", "PREVIOUSLY_MET")
        writer.remember_relationship("Avery Example", "FIRST_LEARNED")
        writer.set_strategy("remote")
        writer.close()
        self.original_bytes = self.path.read_bytes()
        self.source = PrivateStore(self.path, key=self.state_key,
                                   identity_key=self.identity, read_only=True)
        self.backup = self.root / "snapshots" / "encrypted.fernet"

    def tearDown(self):
        self.source.close()
        self.tmp.cleanup()

    def test_backup_verify_and_restore_to_new_path_preserves_memory(self):
        result = create_encrypted_backup(self.source, self.backup)
        self.assertEqual(result["status"], "ENCRYPTED_SNAPSHOT_CREATED")
        self.assertTrue(self.backup.exists())
        ciphertext = self.backup.read_bytes()
        self.assertNotIn(b"Jordan Example", ciphertext)
        self.assertNotIn(b"SQLite format 3", ciphertext)
        self.assertNotIn(self.state_key, ciphertext)
        verified = verify_encrypted_backup(self.backup, self.state_key, self.identity)
        self.assertEqual(verified["status"], "AUTHENTICATED_SQLITE_BACKUP_VALID")
        recovered_path = self.root / "recovered.sqlite"
        restored = restore_to_new_file(self.backup, recovered_path, self.state_key, self.identity)
        self.assertEqual(restored["status"], "RESTORED_TO_NEW_PRIVATE_PATH")
        with_private = PrivateStore(recovered_path, key=self.state_key,
                                    identity_key=self.identity, read_only=True)
        try:
            self.assertEqual(with_private.check_relationship("Jordan Example")[
                "user_reported_relationship"], "PREVIOUSLY_MET")
            self.assertEqual(with_private.check_relationship("Avery Example")[
                "user_reported_relationship"], "FIRST_LEARNED")
            self.assertEqual(with_private.get_strategy(), "remote")
        finally:
            with_private.close()
        self.assertEqual(self.path.read_bytes(), self.original_bytes)

    def test_original_pre_audit_database_is_backed_up_without_migration(self):
        # Reproduce the user's historical database created before governance_decisions.
        # DROP is done ONLY to a newly created synthetic test database.
        self.source.close()
        with sqlite3.connect(self.path) as writer:
            writer.execute("DROP TABLE governance_decisions")
        self.original_bytes = self.path.read_bytes()
        self.source = PrivateStore(self.path, key=self.state_key,
                                   identity_key=self.identity, read_only=True)
        backup = create_encrypted_backup(self.source, self.backup)
        self.assertEqual(backup["schema_variant"], SCHEMA_LEGACY)
        verified = verify_encrypted_backup(self.backup, self.state_key, self.identity)
        self.assertEqual(verified["schema_variant"], SCHEMA_LEGACY)
        destination = self.root / "legacy-restored.sqlite"
        restored = restore_to_new_file(self.backup, destination,
                                       self.state_key, self.identity)
        self.assertEqual(restored["schema_variant"], SCHEMA_LEGACY)
        reopened = PrivateStore(destination, key=self.state_key,
                                identity_key=self.identity, read_only=True)
        try:
            self.assertEqual(reopened.check_relationship("Jordan Example")[
                "user_reported_relationship"], "PREVIOUSLY_MET")
            self.assertEqual(reopened.check_relationship("Avery Example")[
                "user_reported_relationship"], "FIRST_LEARNED")
            self.assertEqual(reopened.get_strategy(), "remote")
            self.assertIsNone(reopened.db.execute(
                "SELECT name FROM sqlite_master WHERE name='governance_decisions'"
            ).fetchone())
        finally:
            reopened.close()
        self.assertEqual(self.path.read_bytes(), self.original_bytes)

    def test_missing_original_base_table_remains_invalid(self):
        self.source.close()
        with sqlite3.connect(self.path) as writer:
            writer.execute("DROP TABLE preferences")
        self.source = PrivateStore(self.path, key=self.state_key,
                                   identity_key=self.identity, read_only=True)
        with self.assertRaisesRegex(ValueError, "required private-memory tables"):
            create_encrypted_backup(self.source, self.backup)
        self.assertFalse(self.backup.exists())

    def test_current_schema_reports_current_variant(self):
        result = create_encrypted_backup(self.source, self.backup)
        self.assertEqual(result["schema_variant"], SCHEMA_CURRENT)
        verified = verify_encrypted_backup(self.backup, self.state_key, self.identity)
        self.assertEqual(verified["schema_variant"], SCHEMA_CURRENT)

    def test_never_overwrite_snapshot_or_existing_restored_file(self):
        create_encrypted_backup(self.source, self.backup)
        with self.assertRaises(FileExistsError):
            create_encrypted_backup(self.source, self.backup)
        with self.assertRaises(FileExistsError):
            restore_to_new_file(self.backup, self.path, self.state_key, self.identity)
        self.assertEqual(self.path.read_bytes(), self.original_bytes)

    def test_wrong_or_missing_keys_and_corruption_fail_closed(self):
        create_encrypted_backup(self.source, self.backup)
        with self.assertRaisesRegex(ValueError, "Identity key"):
            verify_encrypted_backup(self.backup, self.state_key, "z"*64)
        with self.assertRaisesRegex(ValueError, "authentication failed"):
            verify_encrypted_backup(self.backup, Fernet.generate_key(), self.identity)
        with self.assertRaises(RuntimeError):
            verify_encrypted_backup(self.backup, self.state_key, None)
        token = self.backup.read_bytes()
        self.backup.write_bytes(token[:-5] + b"broken")
        with self.assertRaisesRegex(ValueError, "authentication failed"):
            verify_encrypted_backup(self.backup, self.state_key, self.identity)
        missing_target = self.root / "should-not-exist.sqlite"
        with self.assertRaises(ValueError):
            restore_to_new_file(self.backup, missing_target, self.state_key, self.identity)
        self.assertFalse(missing_target.exists())

    def test_missing_backup_and_public_checkout_paths_rejected(self):
        with self.assertRaises(FileNotFoundError):
            verify_encrypted_backup(self.root / "missing.fernet",
                                    self.state_key, self.identity)
        with self.assertRaises(ValueError):
            create_encrypted_backup(self.source, REPO / "backup.fernet")

if __name__ == "__main__":
    unittest.main()
