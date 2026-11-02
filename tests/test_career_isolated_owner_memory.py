"""Isolated end-to-end protected store rehearsal with synthetic people and keys.

No real DPAPI files, no network, no Codex, no live user data, no outbound actions.
"""
from cryptography.fernet import Fernet
import hashlib
import tempfile
import unittest
from pathlib import Path

from outreach_agent.state import PrivateStore
from outreach_agent.career_owner_journal import (
    append_owner_preference, verify_owner_journal,
)
from outreach_agent.career_source_witness import (
    sign_witness, digest,
)
from scripts.assess_career_opportunities_v22 import assess_v22_packet
from test_career_contribution import fixture, pack


class IsolatedMemoryBoundaryTests(unittest.TestCase):
    def test_read_only_existing_relationship_matches_signed_preference(self):
        with tempfile.TemporaryDirectory() as scratch:
            path = Path(scratch) / "synthetic-relationships.sqlite"
            encryption_key = Fernet.generate_key()
            identity_key = b"synthetic-identity-reference-only-000001"
            writer=PrivateStore(path,key=encryption_key,identity_key=identity_key)
            try:
                writer.remember_relationship("Pat Example","PREVIOUSLY_MET",
                    profile_url="https://example.org/professional/pat-example")
            finally:
                writer.close()
            before = hashlib.sha256(path.read_bytes()).hexdigest()
            reader=PrivateStore(path,key=encryption_key,
                                identity_key=identity_key,read_only=True)
            try:
                status=reader.check_relationship("Pat Example",
                    profile_url="https://example.org/professional/pat-example")
            finally:
                reader.close()
            self.assertEqual(status["result"],"EXISTING_RELATIONSHIP")
            self.assertFalse(status["granted_contact_readiness"])
            self.assertEqual(before,hashlib.sha256(path.read_bytes()).hexdigest())
            packet=pack([fixture()])
            report=assess_v22_packet(packet)
            observed=[{
                "index":i, "claim_id":c["claim_id"],"url":c["source_url"],
                "status":"HOST_NOT_APPROVED","source_sha256":None,
            } for i,rec in enumerate(packet["opportunities"]) for c in rec["claims"]]
            receipt=sign_witness({
                "project_id":"PERSONAL_CAREER_OUTREACH","run_id":packet["run_id"],
                "packet_sha256":digest(packet),"results":observed,
                "all_source_text_reproduced":False,
                "source_truth_independently_verified":False,
            },identity_key)
            decision=append_owner_preference(
                Path(scratch)/"research-decisions",identity_key,
                report=report,witness=receipt,index=0,
                decision="RESEARCH_MORE",reason="SOURCE_GAP",
                memory_result=status,consent=True)
            self.assertEqual(decision["decision_recorded"],"RESEARCH_MORE")
            self.assertFalse(decision["contact_ready"])
            self.assertFalse(decision["send_authorized"])
            self.assertEqual(verify_owner_journal(
                Path(scratch)/"research-decisions",identity_key)["verified_events"],1)
            self.assertEqual(before,hashlib.sha256(path.read_bytes()).hexdigest())

    def test_synthetic_private_opt_out_blocks_pursue(self):
        with tempfile.TemporaryDirectory() as scratch:
            path=Path(scratch)/"synthetic.sqlite"
            key=Fernet.generate_key()
            identity=b"synthetic-owner-identity-key-000000001"
            store=PrivateStore(path,key=key,identity_key=identity)
            try:
                store.remember_relationship("Pat Example","PREVIOUSLY_MET")
                row=store.match({"person_name":"Pat Example"})[0]
                store.record_event(row["person_id"],"OPTED_OUT")
            finally:
                store.close()
            check=PrivateStore(path,key=key,identity_key=identity,read_only=True)
            try:
                status=check.check_relationship("Pat Example")
            finally:
                check.close()
            self.assertTrue(status["suppressed"])
            self.assertFalse(status["granted_contact_readiness"])

if __name__=="__main__":
    unittest.main()
