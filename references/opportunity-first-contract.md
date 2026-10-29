# V1.1 — Organization-first permanent leadership qualification

**Purpose:** Find organizations where Fadi could join an internal leadership team. Not Nova Compute business development, external consulting sales, or subcontracting.

## Tracks and sequence
60% AI Strategy & Transformation, 40% Enterprise Product Leadership. Tucson and Southern Arizona first, feasible US-remote next, any industry. In a five-opportunity pilot seek three AI strategy and two product roles, preferably five distinct employers. Honest shortfall beats weak leads.
1. Find and verify a concrete organization initiative, strategy change, product challenge or posted role; record dated public evidence.
2. Assess the specific contribution Fadi could make, a plausible permanent leadership mandate, skills fit, employer feasibility and work mode. An AI initiative does NOT imply the organization lacks a strategy or wants to hire.
3. Classify the opportunity before finding any executive. Verify the accountable initiative owner or credible hiring sponsor, not merely CEO prestige.
4. Establish a person-specific professional route and a credible executive conversation thesis.
5. Apply dual scoring, portfolio diversity, protected owner-memory screening and independent human review; never send.

## Evidence classes
- O1: Verified-on-source posted leadership opening. Require current role posting URL. Its content still requires independent review.
- O2A: Explicit emerging leadership mandate. Public source must actually announce role creation; owner-reported role discussion cannot be authenticated by a model and remains private-review HOLD.
- O2B: Source-supported strategy exploration with a relevant accountable executive. **Hiring UNCONFIRMED**, not a vacancy or established unmet need.
- O3: Broad organizational relevance without actionable mandate. Research backlog.
- O4: Unsuitable, infeasible or materially unreliable. Hold/reject.

## V1.1 scoring and hard gates
Organization /100: strategic signal 30, experience fit 25, permanent leadership feasibility 20, timeliness 15, work mode 10. Proposed minimum 75.
Decision-maker /100: influence 30, documented initiative ownership 25, substantive conversation 20, route 15, role evidence 10. Proposed minimum 70.
Analyst estimates, **not** predictive confidence. Scores never override unsupported hiring, incorrect current role, inaccessible person, missing route, source freshness, career fit, scope or memory HOLD. Do not use AI keyword volume, title prestige or text length as surrogates for hiring potential.

## Structural contract
See outreach_agent/opportunity_qualification.py and the synthetic test fixtures. The exact new public record keys are schema_version, project_id, track, classification, organization, strategic_signal, mandate, fit, decision_maker, scores. The evaluator only returns SHORTLIST_PENDING_HUMAN_REVIEW, EXPLORATORY_REVIEW, or RESEARCH_HOLD; all have confirmed_new=false, contact_ready=false, send_authorized=false. It validates URLs structurally but **cannot visit a web page or verify hiring**.

## Compatibility and rollout
Keep outreach_agent/drive_review_packet.py, its exact JSON/19-column public Google review mapping, and all protected person memory / DPAPI / no-send gates unchanged. V1.1 opportunity records are NOT supported fields in that importer. A human must map reviewed individual evidence to existing permitted fields separately and run owner-only memory reconciliation. Never store private relationships, correspondence or employer discussion notes in PUBLIC GitHub.

Regression: review the previously researched 10 private prospects without committing their identities to Git; do not allow weak general-interest contacts to become invented hiring opportunities. Then supervised five-opportunity pilot, aim 3/2 and distinct employers, independent role/route truth checks, 4/5 Fadi-rated worthwhile conversations as a provisional quality target. Still require P4/P5 native-skill proof, seven consecutive daily runs, >=40 independently reviewed real people and zero unauthorized sends.
