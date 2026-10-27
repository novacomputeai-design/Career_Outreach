import unittest
from outreach_agent.contracts import validate_prospect,validator

class ContractTests(unittest.TestCase):
    def test_schema_is_valid(self):
        self.assertIsNotNone(validator())
    def test_empty_or_unverified_record_cannot_pass(self):
        self.assertTrue(validate_prospect({}))
    def test_malformed_scores_block(self):
        from outreach_agent.pipeline import audit_record
        record={"scores":{"alignment":900}}
        self.assertFalse(audit_record(record))
