import unittest
from outreach_agent.research import Source, BoundedSearch, BoundedExtractor, BudgetExceeded, source_recent_enough
class FakeSearch:
    def search(self,*a,**kw): return []
class FakeExtractor:
    def people(self,*a,**kw): return []
class BudgetAndFreshnessTests(unittest.TestCase):
    def test_hard_search_limit(self):
        b=BoundedSearch(FakeSearch(),max_calls=1)
        b.search("one")
        with self.assertRaises(BudgetExceeded): b.search("two")
    def test_hard_extraction_limit(self):
        b=BoundedExtractor(FakeExtractor(),max_calls=1)
        b.people(None)
        with self.assertRaises(BudgetExceeded): b.people(None)
    def test_stale_role_source_rejected(self):
        old=Source("https://fictional-corporate.test/bio","Old biography",
                   "Legacy executive biography for a test role.", "2026-10-27","2020-01-01")
        self.assertFalse(source_recent_enough(old))
    def test_undated_role_is_not_automatically_current(self):
        undated=Source("https://fictional-corporate.test/team","Undated team page",
                       "Synthetic team text for a unit test.", "2026-10-27")
        self.assertTrue(source_recent_enough(undated)) # UNKNOWN freshness, not confirmed current
