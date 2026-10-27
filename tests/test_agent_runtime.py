"""Offline behavior tests with deliberately SYNTHETIC people and sources."""
import os
import tempfile
import unittest
from pathlib import Path
from cryptography.fernet import Fernet
from outreach_agent.state import PrivateStore
from outreach_agent.research import Source, extract_supported, qualified_source_pair
from outreach_agent.pipeline import make_brief, audit_record, deterministic_score

ROLE="Avery Example is Vice President Product at Fabricated Systems."
INIT="Fabricated Systems leads enterprise product platform modernization and AI automation innovation strategy across operating teams."
S1=Source("https://fabricated-systems.test/leadership", "Leaders", ROLE+" "+INIT, "2026-10-27")
S2=Source("https://fictional-conference.test/speakers", "Speakers", ROLE+" "+INIT, "2026-10-27")
CONTACT=Source("https://fabricated-systems.test/contact-us", "Contact Us",
               "Contact the Fabricated Systems organization through this official contact form.", "2026-10-27")
RAW={"person_name":"Avery Example","current_title":"Vice President Product",
     "organization":"Fabricated Systems","role_quote":ROLE,
     "initiative_quote":INIT,"why_connect":"Discuss enterprise product strategy and modernization with a relevant leader.",
     "segment":"tucson","category":"hiring-influencer"}

class MockSearch:
    def search(self,query,limit=8):
        if "official website contact" in query:
            return [CONTACT]
        if '"Avery Example"' in query:
            return [S2]
        return [S1]

class MockExtractor:
    def people(self,source):
        return [dict(RAW)] if source.url==S1.url else []

class AgentRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.store=PrivateStore(Path(self.tmp.name)/"private.db",
                                key=Fernet.generate_key(),
                                identity_key="a"*64)
    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def test_source_excerpt_must_be_verbatim(self):
        self.assertIsNotNone(extract_supported(S1,RAW))
        bad=dict(RAW,role_quote="Avery Example is Chief Executive Officer at Fabricated Systems.")
        self.assertIsNone(extract_supported(S1,bad))

    def test_corrob_must_be_independent_host(self):
        self.assertTrue(qualified_source_pair({"source_url":S1.url,
            "person_name":"Avery Example","current_title":"Vice President Product"}, S2,ROLE))
        self.assertFalse(qualified_source_pair({"source_url":S1.url,
            "person_name":"Avery Example","current_title":"Vice President Product"}, S1,ROLE))

    def test_full_mock_pipeline_honest_shortfall(self):
        result=make_brief(MockSearch(),MockExtractor(),self.store,
                          target=20,max_queries=1,max_enrich=5)
        self.assertEqual(result["discoveries"],1)
        self.assertEqual(result["new_contact_ready"],1)
        self.assertEqual(result["shortfall"],19)
        self.assertEqual(result["confirmed_sent"],0)
        self.assertEqual(result["audit_status"],"DETERMINISTIC_EVIDENCE_PRECHECK_ONLY")
        self.assertTrue(audit_record(result["candidates"][0]))
        self.assertEqual(result["production_verified_contact_ready"],0)
        saved=self.store.latest_report()
        self.assertEqual(saved["run_id"],result["run_id"])

    def test_same_person_next_run_is_suppressed(self):
        for day in range(7):
            result=make_brief(MockSearch(),MockExtractor(),self.store,
                              target=20,max_queries=1,max_enrich=5)
            self.assertEqual(result["new_contact_ready"],1 if day==0 else 0)

    def test_no_contact_source_blocks(self):
        class NoRoute(MockSearch):
            def search(self,query,limit=8):
                if "official website contact" in query:
                    return []
                return super().search(query,limit)
        result=make_brief(NoRoute(),MockExtractor(),self.store,
                          target=20,max_queries=1,max_enrich=5)
        self.assertEqual(result["new_contact_ready"],0)
        self.assertIn("no_evidenced_official_contact_route",str(result["held"]))

    def test_second_source_missing_blocks(self):
        class OneSource(MockSearch):
            def search(self,query,limit=8):
                if '"Avery Example"' in query:
                    return [S1]
                return super().search(query,limit)
        result=make_brief(OneSource(),MockExtractor(),self.store,
                          target=20,max_queries=1,max_enrich=5)
        self.assertEqual(result["new_contact_ready"],0)
        self.assertIn("no_independent_role_corroboration",str(result["held"]))

    def test_score_has_upper_bounds(self):
        x=extract_supported(S1,RAW)
        x["route_type"]="INDIRECT"
        scores,total=deterministic_score(x)
        self.assertLessEqual(total,100)
        self.assertLessEqual(scores["reachability"],15)

if __name__=="__main__":
    unittest.main()
