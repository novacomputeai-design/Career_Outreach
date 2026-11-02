"""Synthetic legacy-schema migration qualification: never touches actual user memory."""
from __future__ import annotations
import sqlite3
from contextlib import closing
import tempfile
import unittest
from pathlib import Path

from cryptography.fernet import Fernet
from outreach_agent.memory_schema import (
    inspect_memory_schema, migrate_governance_schema, SCHEMA_LEGACY, SCHEMA_CURRENT)
from outreach_agent.state import PrivateStore
from outreach_agent.governance import active_policy

class OwnerMigrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.dbpath = self.root / "synthetic-private.sqlite"
        self.backups = self.root / "backups"
        self.key = Fernet.generate_key()
        self.identity = "r" * 64
        owner = PrivateStore(self.dbpath, key=self.key, identity_key=self.identity)
        owner.remember_relationship("Jordan Synthetic", "PREVIOUSLY_MET")
        owner.remember_relationship("Avery Synthetic", "FIRST_LEARNED")
        owner.set_strategy("remote")
        owner.close()
        with closing(sqlite3.connect(self.dbpath)) as db:
            db.execute("DROP TABLE governance_decisions")
        self.before = inspect_memory_schema(self.dbpath)

    def tearDown(self):
        self.tmp.cleanup()

    def test_owner_only_migration_creates_verified_backup_and_audit(self):
        self.assertEqual(self.before["schema_variant"], SCHEMA_LEGACY)
        report = migrate_governance_schema(self.dbpath,self.backups,self.key,self.identity)
        self.assertEqual(report["status"],"GOVERNANCE_AUDIT_SCHEMA_ADDED")
        self.assertTrue(report["backup_verified_before_change"])
        self.assertTrue(report["original_relationship_row_counts_unchanged"])
        self.assertEqual(report["schema_variant"], SCHEMA_CURRENT)
        self.assertTrue(Path(report["backup_file"]).is_file())
        after = inspect_memory_schema(self.dbpath)
        self.assertEqual(after["existing_record_counts"],self.before["existing_record_counts"])
        self.assertEqual(after["schema_variant"], SCHEMA_CURRENT)
        store=PrivateStore(self.dbpath,key=self.key,identity_key=self.identity,read_only=True)
        try:
            self.assertEqual(store.check_relationship("Jordan Synthetic")[
                "user_reported_relationship"],"PREVIOUSLY_MET")
            self.assertEqual(store.check_relationship("Avery Synthetic")[
                "user_reported_relationship"],"FIRST_LEARNED")
            self.assertEqual(store.get_strategy(),"remote")
            decisions=store.recent_governance_decisions()
            self.assertEqual(len(decisions),1)
            self.assertEqual(decisions[0]["action"],"SCHEMA_MIGRATION")
            self.assertEqual(decisions[0]["policy_version"],active_policy()["version"])
            self.assertEqual(decisions[0]["decision"],"OWNER_INITIATED_APPLIED")
        finally:
            store.close()

    def test_current_database_is_idempotent_without_new_backup(self):
        migrate_governance_schema(self.dbpath,self.backups,self.key,self.identity)
        before=set(self.backups.glob("*.fernet"))
        report=migrate_governance_schema(self.dbpath,self.backups,self.key,self.identity)
        self.assertEqual(report["status"],"ALREADY_CURRENT_NO_CHANGES")
        self.assertFalse(report["database_modified"])
        self.assertEqual(before,set(self.backups.glob("*.fernet")))

    def test_wrong_key_refuses_without_modifying_live_database(self):
        with self.assertRaises(Exception):
            migrate_governance_schema(self.dbpath,self.backups,Fernet.generate_key(),
                                      self.identity)
        self.assertEqual(inspect_memory_schema(self.dbpath)["schema_variant"],SCHEMA_LEGACY)

    def test_missing_original_core_table_holds(self):
        with closing(sqlite3.connect(self.dbpath)) as db:
            db.execute("DROP TABLE preferences")
        with self.assertRaisesRegex(ValueError,"required private-memory tables"):
            migrate_governance_schema(self.dbpath,self.backups,self.key,self.identity)
        self.assertEqual(list(self.backups.glob("*.fernet")),[])

    def test_inspection_never_writes_or_requires_keys(self):
        before=self.dbpath.read_bytes()
        status=inspect_memory_schema(self.dbpath)
        self.assertFalse(status["database_modified"])
        self.assertEqual(self.dbpath.read_bytes(),before)

if __name__ == "__main__":
    unittest.main()
