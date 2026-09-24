# Unit 2 baseline review

Evidence: `unit2_before_evidence.json` and `run_2026-09-23_1947_before.md`.
Reviewer: Codex, with claim-by-claim inspection of the original source files.
These are AI-assisted judgments, not scores produced by an implemented scorer.py
or a claim that the student independently reviewed each answer.

15 fresh answers were returned. There were **17 outgoing attempts**, because
question 5, run 3 encountered two rate-limit responses before succeeding.
Caching was disabled by `run_eval.py::run_once`; retries are not extra trials.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every substantive answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunks contain a complete, identifiable thought | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Every factual claim is supported by its citation | 4 of 5 | 4/5 | 4/5 | 4/5 | MET |

Criterion 3 repeats a single deterministic gate measurement. The full application
was also exercised: all five actual refusal strings matched `gate.REFUSAL`, with
zero generation calls. Criterion 4 was sampled three times and the deterministic
chunks were identical. Generated answers are three distinct uncached trials.

## Retrieval and claim review, all three runs

| Question | Retrieved supporting file | Supported claims in every run | C1 | C2 | C5 |
|---|---|---|---|---|---|
| 1: lottery | admin_housing_lottery.txt | Credits rank juniors/seniors first; ties break randomly | PASS ×3 | PASS ×3 | PASS ×3 |
| 2: Aldridge wash | housing_aldridge_hall_laundry.txt; housing_aldridge_hall.txt | Wash $1.75; payment card only (both files support both facts) | PASS ×3 | PASS ×3 | PASS ×3 |
| 3: late drop | admin_add_drop_deadline.txt | Drop after week two shows W | PASS ×3 | PASS ×3 | PASS ×3 |
| 4: printing | admin_printing_quota.txt | $30 of printing per semester | PASS ×3 | PASS ×3 | PASS ×3 |
| 5: Morrow damp | housing_morrow_house.txt | Ground-floor damp; two rooms offline in 2024; causal connection is NOT explicitly stated | PASS ×3 | PASS ×3 | FAIL ×3 |

The relevant excerpts, checked against the source files, are:

```text
admin_housing_lottery.txt:
Rising sophomores get a number drawn at random, but juniors and seniors are ordered by accumulated credit hours first, and only tie-break randomly.

housing_aldridge_hall_laundry.txt:
Machines take $1.75 wash, $1.50 dry, card only.

housing_aldridge_hall.txt:
Laundry costs $1.75 wash, $1.50 dry, card only.

admin_add_drop_deadline.txt:
Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript.

admin_printing_quota.txt:
Every student gets $30 of printing per semester, which is roughly 600 black-and-white pages.

housing_morrow_house.txt:
The bad: known damp problem on the ground floor; two rooms were taken offline in 2024.
```

## Chunk review

All three samples have the following five chunks. The repeated wording of the
BIOL post ("I lived here") is awkward source text, but the title identifies the
course, the chunk contains complete facts, and the chunker did not cut a sentence.
This criterion measures boundaries and context, not factual accuracy of the corpus.

| Source (chunk 0 in each file) | Subject identifiable | Complete factual statement | No splitting-induced fragment |
|---|---|---|---|
| admin_add_drop_deadline.txt | Yes: title names add/drop | Yes: add through week two | Yes |
| course_biol_160.txt | Yes: BIOL 160 title | Yes: lecture three times weekly | Yes |
| course_hist_118_workload.txt | Yes: HIST 118 title | Yes: about 120 pages weekly | Yes |
| dining_pellew_dining_hall_followup.txt | Yes: Pellew title and body | Yes: peak wait 12–18 minutes | Yes |
| housing_innisfree_hall.txt | Yes: Innisfree title | Yes: doubles sharing a bathroom | Yes |

## Diagnosis and pre-change plan

No criterion misses its aggregate target, but question 5 fails the claim-support
check in **all three baseline runs**. Its answer says:

```text
A known damp problem was reported on the ground floor of Morrow House, which resulted in two rooms being taken offline in 2024.

Sources: housing_morrow_house.txt
```

**Stage: generation. Mechanism:** the model connects two adjacent source facts
with "which resulted in," turning co-occurrence into a causal assertion. The
retrieved chunk contains both original facts, so missing retrieval or broken
chunk boundaries do not explain this failure. The source's semicolon suggests
an association, but does not explicitly state or logically require causation.
Under criterion 5's existing explicit-support/direct-entailment rule, I count
that causal link as unsupported. This is a strict, disclosed reading, not a
keyword failure or a newly lowered target.

The criterion still passes 4/5, which exposes a permissive target: it tolerates
a repeated unsupported claim on the same question. For a future evaluation I
would consider requiring 5/5 claim-supported answers in each run. I am **not**
changing the existing criterion or verdict retrospectively.

**One planned change:** add one grounding-prompt rule forbidding unstated causal
inferences and requiring adjacent observations to remain separate unless the
source explicitly connects them. Keep the corpus, chunker, embedding model,
generation model, top-k, cutoff, questions and targets unchanged. Prediction:
question 5 stops asserting causation, taking criterion 5 from 4/5 to 5/5, while
criteria 1–4 remain unchanged. This could fail because a prompt is a soft control;
three improved answers would still be only limited evidence, not a guarantee.
