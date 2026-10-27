"""Mock HTTP provider; prove missing auth and unsupported source claims never pass."""
import os
import unittest
from unittest.mock import patch
from outreach_agent.research import Tavily, Source, url_valid, extract_supported

class FakeResponse:
    def raise_for_status(self): pass
    def json(self):
        return {"results":[
            {"url":"https://firm.test/leadership","title":"Leadership",
             "content":"This is a synthetic corporate leadership page with a named executive."},
            {"url":"https://www.linkedin.com/in/synthetic-person","title":"LinkedIn",
             "content":"Provider should skip social profile automated processing."},
            {"url":"http://insecure.test","title":"HTTP page","content":"should skip insecure URLs"}
        ]}
class FakeSession:
    def post(self,*a,**kw):
        return FakeResponse()

class AdapterTests(unittest.TestCase):
    def test_missing_tavily_key_blocks(self):
        with patch.dict(os.environ,{},clear=True):
            with self.assertRaises(RuntimeError):
                Tavily()
    def test_filters_linkedin_and_untrusted_scheme(self):
        search=Tavily(key="synthetic-key",session=FakeSession())
        result=search.search("synthetic")
        self.assertEqual([r.url for r in result],["https://firm.test/leadership"])
    def test_url_format_not_proof(self):
        self.assertTrue(url_valid("https://firm.test/leadership"))
        self.assertFalse(url_valid("https://example.org/team"))
        self.assertFalse(url_valid("https://127.0.0.1/private"))
        self.assertIsNone(extract_supported(Source("https://firm.test", "X", "No executive identity here", "2026-10-27"),
            {"person_name":"Some Executive","current_title":"CTO"}))

if __name__=="__main__":
    unittest.main()
