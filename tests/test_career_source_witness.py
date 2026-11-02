"""Owner-side public-text witness tests; no external network or private keys."""
import copy
import unittest

from outreach_agent.career_source_witness import (
    witness_sources, sign_witness, verify_witness, safe_public_host,
)
from test_career_contribution import fixture, pack

IP = lambda host,port,**kwargs: [(2,1,0,"",("93.184.216.34",443))]


class WitnessTests(unittest.TestCase):
    def test_reproduces_exact_claim_but_not_semantic_truth(self):
        p=pack([fixture()])
        pages={c["source_url"]: (c["excerpt"]+" "+c["claim_text"],"text/plain")
               for c in p["opportunities"][0]["claims"]}
        r=witness_sources(p,{"employer.example"},fetch=lambda u:pages[u],resolver=IP)
        self.assertTrue(r["all_source_text_reproduced"])
        self.assertFalse(r["source_truth_independently_verified"])
        self.assertFalse(r["contact_ready"])
        signed=sign_witness(r,b"A"*32)
        self.assertTrue(verify_witness(signed,p,b"A"*32))
        other=copy.deepcopy(p)
        other["run_id"]="replayed-different-run"
        self.assertFalse(verify_witness(signed,other,b"A"*32))
        self.assertFalse(verify_witness(signed,p,b"B"*32))

    def test_host_not_approved_fetcher_never_invoked(self):
        p=pack([fixture()])
        def fail(_):
            raise AssertionError("MUST_NOT_FETCH")
        r=witness_sources(p,{"bannerhealth.com"},fetch=fail,resolver=IP)
        self.assertTrue(all(x["status"]=="HOST_NOT_APPROVED" for x in r["results"]))

    def test_private_address_rejected(self):
        private=lambda host,port,**kw:[(2,1,0,"",("127.0.0.1",443))]
        self.assertFalse(safe_public_host("https://example.com/e",{"employer.example"},resolver=private))
        self.assertFalse(safe_public_host("https://127.0.0.1/a",{"127.0.0.1"},resolver=IP))
        self.assertFalse(safe_public_host("https://example.com:8080/a",{"employer.example"},resolver=IP))
        self.assertFalse(safe_public_host("http://example.com/a",{"employer.example"},resolver=IP))

    def test_altered_claim_excerpt_fails_text_check(self):
        p=pack([fixture()])
        c=p["opportunities"][0]["claims"][0]
        pages={cl["source_url"]:("Unrelated public article","text/plain")
               for cl in p["opportunities"][0]["claims"]}
        r=witness_sources(p,{"employer.example"},fetch=lambda u:pages[u],resolver=IP)
        self.assertFalse(r["all_source_text_reproduced"])
        self.assertEqual(r["results"][0]["status"],"TEXT_NOT_FOUND")

    def test_unavailable_source_is_hold_not_verification(self):
        p=pack([fixture()])
        def unavailable(url):
            raise ValueError("HTTP 403")
        r=witness_sources(p,{"employer.example"},fetch=unavailable,resolver=IP)
        self.assertTrue(all(x["status"]=="FETCH_UNAVAILABLE" for x in r["results"]))

if __name__ == "__main__":
    unittest.main()
