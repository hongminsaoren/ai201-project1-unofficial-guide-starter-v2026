# Unit 2 after review and paired scoring ledger

Reviewer: Codex. These are AI-assisted semantic judgments of the actual saved
answers, checked against the original source files. There is no automatic
semantic scorer.py. The baseline review contains the source passages and
chunk-by-chunk checklist; the retrieval evidence and chunk samples are exactly
identical after the change.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every substantive answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunks preserve a complete, identifiable thought | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Every factual claim is supported by its citation | 4 of 5 | 4/5 | 4/5 | 5/5 | MET |

## Each question in each run

C1 (answer-bearing retrieval) and C2 (source present in generated text) pass for
every entry below, before and after. The table records C5 (all claims supported).
A model-written Sources line counts as part of its answer; the CLI's separately
printed retrieved-source list is not used to satisfy C2.

| Question | Run | Before C5 | After C5 | Reason |
|---|---|---|---|---|
| 1 | 1 | PASS | PASS | Credit-hour priority and random tie-breaking supported by admin_housing_lottery.txt. |
| 1 | 2 | PASS | PASS | Credit-hour priority and random tie-breaking supported by admin_housing_lottery.txt. |
| 1 | 3 | PASS | PASS | Credit-hour priority and random tie-breaking supported by admin_housing_lottery.txt. |
| 2 | 1 | PASS | PASS | Wash price $1.75 and card-only payment supported by both Aldridge citations. |
| 2 | 2 | PASS | PASS | Wash price $1.75 and card-only payment supported by both Aldridge citations. |
| 2 | 3 | PASS | PASS | Wash price $1.75 and card-only payment supported by both Aldridge citations. |
| 3 | 1 | PASS | PASS | Transcript W after week two supported by admin_add_drop_deadline.txt. |
| 3 | 2 | PASS | PASS | Transcript W after week two supported by admin_add_drop_deadline.txt. |
| 3 | 3 | PASS | PASS | Transcript W after week two supported by admin_add_drop_deadline.txt. |
| 4 | 1 | PASS | PASS | Semester printing allowance $30 supported by admin_printing_quota.txt. |
| 4 | 2 | PASS | PASS | Semester printing allowance $30 supported by admin_printing_quota.txt. |
| 4 | 3 | PASS | PASS | Semester printing allowance $30 supported by admin_printing_quota.txt. |
| 5 | 1 | FAIL | FAIL | Both answers infer damp caused room closures; source does not explicitly connect them. |
| 5 | 2 | FAIL | FAIL | Both answers infer damp caused room closures; source does not explicitly connect them. |
| 5 | 3 | FAIL | PASS | After answer reports only ground-floor damp; baseline adds unsupported causation. |

## Claim-level after review for Morrow House

Runs 1 and 2 each make three claims: ground-floor damp (supported), two rooms
were taken offline in 2024 (supported), and damp caused those closures (not
explicitly stated or entailed). Therefore the whole answer fails C5. Run 3
contains only the supported damp claim and cites housing_morrow_house.txt;
it passes. No answer was replaced or retried to obtain a better score.

## Unchanged deterministic checks

All five OUT_OF_SCOPE questions return the exact refusal string with zero model
calls. All five samples meet the three C4 checks in each of three repeated
samples. Their full text appears in unit2_after_evidence.json; it matches baseline.
The original criteria and question file hashes also match between conditions.

## Measured effect

Before C5: 4/5, 4/5, 4/5. After C5: 4/5, 4/5, 5/5.
Unsupported answers fell from 3/15 to 2/15 (Morrow House: 3/3 to 2/3).
All five aggregate criteria remain MET. This is a small observed difference, not
proof of a reliable improvement: one response changed, the sample is small, and
model randomness could explain the difference. Prompt-only grounding still fails.
