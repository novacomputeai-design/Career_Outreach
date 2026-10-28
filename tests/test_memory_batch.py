"""Synthetic private-memory batch regression tests. No real people or API calls."""
import json
import tempfile
import unittest
from pathlib import Path
from cryptography.fernet import Fernet
from outreach_agent.state import PrivateStore
from outreach_agent.memory_batch import screen_batch, MAX_PEOPLE, MAX_BYTES

class OperatorBatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)
        self.store = PrivateStore(self.path / "protected.sqlite",
                                  key=Fernet.generate_key(),identity_key="x"*64)
        self.store.remember_relationship("Jordan Example", "PREVIOUSLY_MET")
        self.store.remember_relationship("Avery Example", "FIRST_LEARNED")

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def write(self, data):
        p = self.path / "names.json"
        p.write_text(json.dumps(data),encoding="utf-8")
        return p

    def test_known_unknown_and_duplicate_are_distinct(self):
        p = self.write([
            "Jordan Example", {"person_name":"Avery Example"}, "New Synthetic",
            "Jordan Example"
        ])
        result = screen_batch(self.store,p)
        self.assertEqual(result["people_checked"], 4)
        self.assertEqual(result["new_contact_ready_granted"],0)
        self.assertFalse(result["complete_cross_channel_history_verified"])
        self.assertEqual([x["result"] for x in result["results"]],
                         ["EXISTING_RELATIONSHIP","SEEN_IN_STORE",
                          "NOT_FOUND_IN_LOCAL_STORE","DUPLICATE_IN_BATCH_HOLD"])
        self.assertEqual(result["results"][2]["novelty"],"UNVERIFIED")
        self.assertTrue(all(x["granted_contact_readiness"] is False
                            for x in result["results"]))
        self.assertFalse(any("encrypted" in str(k).lower() or "key" in str(k).lower()
                             for row in result["results"] for k in row))

    def test_opt_out_preserved(self):
        person={"person_name":"Suppressed Example"}
        pid=self.store.register(person)
        self.store.record_event(pid,"OPTED_OUT")
        result=screen_batch(self.store,self.write(["Suppressed Example"]))
        self.assertTrue(result["results"][0]["suppressed"])
        self.assertEqual(result["new_contact_ready_granted"],0)

    def test_reject_extra_fields_and_invalid_profile(self):
        with self.assertRaises(ValueError):
            screen_batch(self.store,self.write([{
                "person_name":"Jordan Example", "secret":"not allowed"
            }]))
        with self.assertRaises(ValueError):
            screen_batch(self.store,self.write([{
                "person_name":"Jordan Example", "profile_url":"http://example.test"
            }]))

    def test_empty_large_and_non_list_fail_closed(self):
        for obj in ([],{},["One"],["Synthetic Example"]*(MAX_PEOPLE+1)):
            with self.subTest(obj_type=str(type(obj)),count=len(obj)):
                with self.assertRaises(ValueError):
                    screen_batch(self.store,self.write(obj))
        p=self.path/"large.json"
        p.write_text(" "*(MAX_BYTES+1),encoding="utf-8")
        with self.assertRaises(ValueError):
            screen_batch(self.store,p)

    def test_missing_file_fails_closed(self):
        with self.assertRaises(FileNotFoundError):
            screen_batch(self.store,self.path/"absent.json")

    def test_no_private_notes_exposed(self):
        result=screen_batch(self.store,self.write(["Jordan Example"]))
        self.assertEqual(set(result["results"][0]),
                         {"person_name","result","novelty","granted_contact_readiness",
                          "user_reported_relationship","suppressed"})
        self.assertNotIn("encrypted_record",str(result))
        self.assertNotIn("events",str(result))

if __name__=="__main__":
    unittest.main()
