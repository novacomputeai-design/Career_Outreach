"""Gate M2 *synthetic* boundary rehearsal, without DPAPI or real network.

These tests exercise the real PrivateStore, recovery, witness and journal
libraries using randomized throwaway secrets outside the repository.
They are NOT owner-Windows or source-truth qualification.
"""
from copy import deepcopy
from cryptography.fernet import Fernet
from pathlib import Path
import secrets
import tempfile
import unittest

from outreach_agent.state import PrivateStore
from outreach_agent.memory_recovery import (
    create_encrypted_backup, verify_encrypted_backup, restore_to_new_file,
)
from outreach_agent.career_source_witness import (
    witness_sources, sign_witness, verify_witness,
)
from outreach_agent.career_owner_journal import (
    append_owner_preference, verify_owner_journal,
    validate_owner_handoff,
)
from scripts.assess_career_opportunities_v22 import assess_v22_packet
from test_career_contribution import fixture, pack


PUBLIC = lambda host, port, **kw: [(2, 1, 0, "", ("93.184.216.34", 443))]


class GateM2SyntheticBoundaryTests(unittest.TestCase):
    def test_recovery_people_witness_journal_and_negative_controls(self):
        with tempfile.TemporaryDirectory(prefix="career-m2-synthetic-") as folder:
            root = Path(folder)
            key = Fernet.generate_key()
            identity = secrets.token_hex(32).encode("ascii")
            source_db = root / "relationships.sqlite"
            writer = PrivateStore(source_db, key=key, identity_key=identity)
            try:
                writer.remember_relationship(
                    "Pat Example", "PREVIOUSLY_MET",
                    profile_url="https://example.org/people/pat-one"
                )
                writer.remember_relationship(
                    "Alex Example", "FIRST_LEARNED",
                    profile_url="https://example.org/people/alex"
                )
                writer.remember_relationship(
                    "Jordan Example", "PREVIOUSLY_MET",
                    profile_url="https://example.org/people/jordan"
                )
                selected = writer.match({"person_name": "Jordan Example"})[0]
                writer.record_event(selected["person_id"], "OPTED_OUT")
            finally:
                writer.close()

            source = PrivateStore(source_db, key=key, identity_key=identity, read_only=True)
            encrypted = root / "backup" / "relationships.fernet"
            try:
                backup = create_encrypted_backup(source, encrypted)
                self.assertEqual(backup["status"], "ENCRYPTED_SNAPSHOT_CREATED")
            finally:
                source.close()
            self.assertEqual(
                verify_encrypted_backup(encrypted, key, identity)["status"],
                "AUTHENTICATED_SQLITE_BACKUP_VALID",
            )
            destination = root / "restored" / "relationships-restored.sqlite"
            self.assertEqual(
                restore_to_new_file(encrypted, destination, key, identity)["status"],
                "RESTORED_TO_NEW_PRIVATE_PATH",
            )
            restored = PrivateStore(destination, key=key, identity_key=identity, read_only=True)
            try:
                met = restored.check_relationship(
                    "Pat Example", profile_url="https://example.org/people/pat-one"
                )
                namesake = restored.check_relationship(
                    "Pat Example", profile_url="https://example.org/people/pat-two"
                )
                first = restored.check_relationship(
                    "Alex Example", profile_url="https://example.org/people/alex"
                )
                opted_out = restored.check_relationship(
                    "Jordan Example", profile_url="https://example.org/people/jordan"
                )
                unknown = restored.check_relationship("Not In Memory")
                self.assertEqual(met["result"], "EXISTING_RELATIONSHIP")
                self.assertEqual(namesake["result"], "POSSIBLE_NAMESAKE_HOLD")
                self.assertEqual(first["result"], "SEEN_IN_STORE")
                self.assertTrue(opted_out["suppressed"])
                self.assertEqual(unknown["novelty"], "UNVERIFIED")
                for status in (met, namesake, first, opted_out, unknown):
                    self.assertFalse(status["granted_contact_readiness"])
            finally:
                restored.close()

            packet = pack([fixture()])
            report = assess_v22_packet(packet)
            # This is a mocked page, not an independent external source.
            pages = {}
            for claim in packet["opportunities"][0]["claims"]:
                pages[claim["source_url"]] = (
                    pages.get(claim["source_url"], ("", "text/plain"))[0]
                    + " " + claim["excerpt"] + " " + claim["claim_text"],
                    "text/plain",
                )
            witness = sign_witness(witness_sources(
                packet, {"employer.example"}, fetch=lambda url: pages[url],
                resolver=PUBLIC,
            ), identity)
            self.assertTrue(verify_witness(witness, packet, identity))
            self.assertFalse(witness["semantic_claims_verified"])
            self.assertFalse(witness["source_truth_independently_verified"])

            other = deepcopy(packet)
            other["run_id"] = "different-synthetic-run"
            self.assertFalse(verify_witness(witness, other, identity))
            tampered = deepcopy(witness)
            tampered["results"][0]["status"] = "FETCH_UNAVAILABLE"
            self.assertFalse(verify_witness(tampered, packet, identity))

            record, assessment, report_hash, witness_hash = validate_owner_handoff(
                report, witness, identity, 0
            )
            self.assertEqual(record["executive"]["name"], "Pat Example")
            self.assertEqual(len(report_hash), 64)
            self.assertEqual(len(witness_hash), 64)

            journal = root / "research-decisions"
            common = dict(report=report, witness=witness, index=0,
                          decision="RESEARCH_MORE", reason="SOURCE_GAP",
                          memory_result=met)
            with self.assertRaisesRegex(ValueError, "EXPLICIT_INTERACTIVE_OWNER_CONSENT_REQUIRED"):
                append_owner_preference(journal, identity, consent=False, **common)
            self.assertEqual(verify_owner_journal(journal, identity)["verified_events"], 0)

            recorded = append_owner_preference(journal, identity, consent=True, **common)
            self.assertEqual(recorded["sequence"], 1)
            self.assertFalse(recorded["contact_ready"])
            self.assertFalse(recorded["send_authorized"])
            self.assertFalse(recorded["application_submitted"])
            self.assertEqual(verify_owner_journal(journal, identity)["verified_events"], 1)
            with self.assertRaisesRegex(ValueError, "OWNER_DECISION_REPLAY_OR_DUPLICATE_REVIEW"):
                append_owner_preference(journal, identity, consent=True, **common)

            with self.assertRaises(ValueError):
                append_owner_preference(
                    root / "suppression-journal", identity, report=report, witness=witness,
                    index=0, decision="PURSUE", reason="LEADERSHIP_SCOPE",
                    memory_result=opted_out, consent=True,
                )
            self.assertEqual(
                verify_owner_journal(root / "suppression-journal", identity)["verified_events"], 0
            )

            original = (journal / "owner-reviews.jsonl").read_text(encoding="utf-8")
            bad_copy = root / "tampered-copy"
            bad_copy.mkdir()
            (bad_copy / "owner-reviews.jsonl").write_text(
                original.replace("SOURCE_GAP", "ROLE_MATCH"), encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "OWNER_DECISION_JOURNAL_INTEGRITY_FAILURE"):
                verify_owner_journal(bad_copy, identity)
            self.assertEqual(verify_owner_journal(journal, identity)["verified_events"], 1)
            self.assertFalse(report["source_truth_independently_verified"])
            self.assertEqual(report["contact_ready"], 0)


if __name__ == "__main__":
    unittest.main()
