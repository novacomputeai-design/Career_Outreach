"""Offline behavior tests with deliberately SYNTHETIC people and sources."""
import os
import tempfile
import unittest
from pathlib import Path
from cryptography.fernet import Fernet
from outreach_agent.state import PrivateStore
from outreach_agent.research import Source, extract_supported, qualified_source_pair
from outreach_agent.pipeline import make_brief, audit_record, deterministic_score, plausible_official_domain

ROLE="Avery Example is Vice President Product at Fabricated Systems."
INIT="Fabricated Systems leads enterprise product platform modernization and AI automation innovation strategy across operating teams."
S1=Source("https://fabricated-systems.test/leadership", "Leaders", ROLE+" "+INIT, "2026-10-27","2026-10-27")
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
        self.assertEqual(result["source_corroborated_pending_human_review"],1)
        self.assertEqual(result["new_contact_ready"],0)
        self.assertEqual(result["shortfall"],20)
        self.assertEqual(result["research_shortfall"],19)
        self.assertEqual(result["confirmed_sent"],0)
        self.assertEqual(result["audit_status"],"DETERMINISTIC_EVIDENCE_PRECHECK_ONLY")
        self.assertTrue(audit_record(result["candidates"][0]))
        self.assertEqual(result["production_verified_contact_ready"],0)
        saved=self.store.latest_report()
        self.assertEqual(saved["run_id"],result["run_id"])

    def test_undated_sources_do_not_establish_current_role(self):
        class UndatedSourceSearch(MockSearch):
            def search(self,query,limit=8):
                results=super().search(query,limit)
                return [Source(x.url,x.title,x.text,x.retrieved_on,None) for x in results]
        result=make_brief(UndatedSourceSearch(),MockExtractor(),self.store,
                          target=5,max_queries=1,max_enrich=5)
        self.assertEqual(result["source_corroborated_pending_human_review"],0)
        self.assertIn("undated_current_role_requires_review",str(result["held"]))

    def test_draft_uses_specific_career_evidence_and_is_not_generic(self):
        lead=dict(extract_supported(S1,RAW))
        lead["route_type"]="INDIRECT"
        from outreach_agent.pipeline import proposal
        draft=proposal(lead)
        self.assertIn("enterprise product platform modernization",draft)
        self.assertIn("Discuss enterprise product strategy",RAW["why_connect"])
        self.assertIn("discuss enterprise product strategy",draft)
        self.assertNotIn("Nova Compute",draft)
        self.assertIn("\\n\\n",draft)

    def test_strong_provisional_score_is_reachable_without_claiming_hiring(self):
        lead=dict(extract_supported(S1,RAW))
        lead["route_type"]="INDIRECT"
        scores,total=deterministic_score(lead)
        self.assertGreaterEqual(total,85)
        self.assertLessEqual(scores["influence"],25)

    def test_same_person_next_run_is_suppressed(self):
        for day in range(7):
            result=make_brief(MockSearch(),MockExtractor(),self.store,
                              target=20,max_queries=1,max_enrich=5)
            self.assertEqual(result["source_corroborated_pending_human_review"],1 if day==0 else 0)
            self.assertEqual(result["new_contact_ready"],0)

    def test_no_contact_source_blocks(self):
        class NoRoute(MockSearch):
            def search(self,query,limit=8):
                if "official website contact" in query:
                    return []
                return super().search(query,limit)
        result=make_brief(NoRoute(),MockExtractor(),self.store,
                          target=20,max_queries=1,max_enrich=5)
        self.assertEqual(result["new_contact_ready"],0)
        self.assertEqual(result["source_corroborated_pending_human_review"],0)
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

    def test_contact_page_from_unrelated_host_not_attributed_to_employer(self):
        self.assertTrue(plausible_official_domain("Fabricated Systems",S1.url))
        self.assertFalse(plausible_official_domain("Fabricated Systems","https://conference-sponsors.test/contact"))

    def test_score_has_upper_bounds(self):
        x=extract_supported(S1,RAW)
        x["route_type"]="INDIRECT"
        scores,total=deterministic_score(x)
        self.assertLessEqual(total,100)
        self.assertLessEqual(scores["reachability"],15)

if __name__=="__main__":
    unittest.main()
