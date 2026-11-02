# Legacy V1/V1.1 personal contact scoring — compatibility only

**V2.1 WARNING:** Do not use person scores, organization scores, or historic 70/75 thresholds to qualify a V2.1 employer opportunity, to grant engagement readiness, or to generate a 20-person quota. See `references/career-intelligence-operating-contract-v2.1.md` and `outreach_agent/career_intelligence.py`. Older scoring exists only for regression tests and the OPTIONAL legacy Python pipeline.

# Provisional evidence-based score
Score each verified individual 0–100; these weights are hypotheses for calibration, not predictive confidence.

| Factor | Maximum | How to substantiate |
|---|---:|---|
| Transferable leadership/capability fit | 30 | Resume evidence + organization's documented need/initiative |
| Decision influence or introductions | 25 | Actual position and documented scope; don't equate title with hiring authority |
| Authentic specific conversation reason | 20 | Concrete topical common interest anchored to verifiable fact |
| Professional reachability | 15 | Verified public direct/indirect/warm/manual route, correctly labeled |
| Work geography / mode | 10 | Tucson preferred; fully remote US qualifies |

>=85 strong; 70–84 qualified; 50–69 research further; <50 reject. Mandatory hard gates override total: verified name/current title/org/source; individualized reason; legitimate route; novelty check; no prior suppression; >=70. When evidence is insufficient HOLD, not inflated. Do not silently raise weights to reach 20/day.

## V1.1 opportunity rubric supersedes legacy *person-only* ranking for hiring research
Use references/opportunity-first-contract.md and config/operating-policy.json opportunity_search. The original 70/100 person score does not demonstrate employer leadership need, actual hiring, a particular sponsor or a strong route. V1.1 uses separate organization >=75 and executive >=70 structural scores plus non-waivable evidence gates and human review; never infer hiring from AI keywords or title prestige.
