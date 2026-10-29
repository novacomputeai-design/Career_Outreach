"""No-private-data Drive review handoff contract and safety regressions."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from outreach_agent.drive_review_packet import (
    build_review_packet, read_input, write_review_packet, PROSPECT_HEADERS, RUN_HEADERS
)
from outreach_agent.project_scope import PROJECT_ID


def fixture():
    return {
        "project_id":PROJECT_ID,"run_id":"pilot-2026-10-28-001",
        "date_local":"2026-10-27",
        "candidates":[{
            "project_id":PROJECT_ID,
            "person_name":"Avery Example",
            "organization":"Synthetic Innovation Center",
            "current_title":"Director of Product",
            "segment":"tucson",
            "category":"strategic-connector",
            "why_connect":"Discuss how enterprise modernization shapes product organizations.",
            "role_source_url":"https://synthetic.example.test/leader",
            "reason_source_url":"https://synthetic.example.test/initiative",
            "observed_on":"2026-10-27",
            "route_type":"INDIRECT",
            "route_url":"https://synthetic.example.test/contact",
            "score_total":82,
        }]
    }


class ReviewPacketTests(unittest.TestCase):
    def test_review_packet_is_unapproved_public_only(self):
        p=build_review_packet(fixture())
        self.assertEqual(p["prospects"][0],PROSPECT_HEADERS)
        self.assertEqual(p["daily_runs"][0],RUN_HEADERS)
        self.assertEqual(p["prospects"][1][10],"PENDING_REVIEW")
        self.assertEqual(p["prospects"][1][11],"UNCHECKED")
        self.assertEqual(p["prospects"][1][12],"UNVERIFIED")
        self.assertEqual(p["prospects"][1][16],"NOT_REVIEWED")
        self.assertEqual(p["daily_runs"][1][7:9],[0,0])
        self.assertEqual(p["manifest"]["new_contact_ready"],0)
        self.assertEqual(p["manifest"]["messages_sent"],0)
        self.assertFalse(p["manifest"]["codex_native_skill_activation_verified"])
        self.assertTrue(p["prospects"][1][0].startswith("RESEARCH-"))

    def test_reject_out_of_scope_even_when_project_id_spoofed(self):
        x=fixture()
        x["candidates"][0]["why_connect"]="Submit our capability statement to the prime contractor"
        with self.assertRaisesRegex(ValueError,"Career purpose HOLD"):
            build_review_packet(x)

    def test_reject_unapproved_private_fields_and_send_claims(self):
        for key in ("private_note","email","approval_granted","messages_sent","opted_out"):
            x=fixture(); x["candidates"][0][key]="leak"
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,"Unrecognized"):
                build_review_packet(x)
        x=fixture();x["project_id"]="NOVA_SUBCONTRACTING"
        with self.assertRaisesRegex(ValueError,"identity mismatch"):
            build_review_packet(x)

    def test_holds_missing_sources_rather_than_invents_proof(self):
        x=fixture()
        x["candidates"][0].pop("role_source_url")
        x["candidates"][0].pop("route_url")
        x["candidates"][0]["route_type"]="NO_ROUTE"
        p=build_review_packet(x)
        self.assertEqual(p["prospects"][1][10],"HOLD")
        self.assertEqual(p["manifest"]["people_held_for_missing_public_evidence"],1)
        self.assertEqual(p["manifest"]["new_contact_ready"],0)

    def test_fails_on_name_duplication_and_guessed_routes(self):
        x=fixture()
        x["candidates"].append(dict(x["candidates"][0]))
        with self.assertRaisesRegex(ValueError,"Duplicate"):
            build_review_packet(x)
        x=fixture()
        x["candidates"][0]["route_url"]="https://jane:pass@example.org/path"
        with self.assertRaisesRegex(ValueError,"HTTPS"):
            build_review_packet(x)

    def test_csv_injection_sanitized_and_no_overwrite(self):
        x=fixture()
        x["candidates"][0]["organization"]="=HYPERLINK('https://bad.example')"
        with tempfile.TemporaryDirectory() as root:
            output=Path(root)/"new-review"
            result=write_review_packet(x,output)
            self.assertEqual(result["messages_sent"],0)
            with (output/"prospects-review.csv").open("r",encoding="utf-8-sig",newline="") as f:
                row=list(csv.reader(f))[1]
            self.assertTrue(row[2].startswith("'="))
            batch=json.loads((output/"candidate-batch.json").read_text(encoding="utf-8"))
            owner=json.loads((output/"candidate-public-review.json").read_text(encoding="utf-8"))
            self.assertEqual(batch[0]["person_name"],"Avery Example")
            self.assertEqual(owner[0]["project_id"],PROJECT_ID)
            self.assertNotIn("private_note",str(owner))
            self.assertNotIn("why_connect",str(batch))
            with self.assertRaises(FileExistsError):
                write_review_packet(x,output)

    def test_read_inputs_from_private_json_only(self):
        with tempfile.TemporaryDirectory() as root:
            source=Path(root)/"research.json"
            source.write_text(json.dumps(fixture()),encoding="utf-8")
            self.assertEqual(read_input(source)["project_id"],PROJECT_ID)

    def test_empty_run_is_honest_not_fake_contacts(self):
        x=fixture(); x["candidates"]=[]
        p=build_review_packet(x)
        self.assertEqual(len(p["prospects"]),1)
        self.assertEqual(p["manifest"]["people_considered"],0)
        self.assertEqual(p["manifest"]["new_contact_ready"],0)


if __name__=="__main__":
    unittest.main()
