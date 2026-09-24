# The Unofficial Guide

# Unit 1

## What This Does

This command-line RAG assistant searches the 88 fictional student-life posts in
`campus_life`. It answers questions about housing, laundry, registration deadlines,
printing and other campus topics using locally embedded document chunks. Chroma
retrieves five chunks with cosine distance, and a gate stops unrelated questions
before Gemini is called. The corpus was written for the course and is not factual
advice about any real university.

### Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Set your own GEMINI_API_KEY in .env, never in a tracked file.
python test.py
python app.py index
python app.py ask "How are juniors and seniors ranked in the housing lottery?"
```

For key-free retrieval: `python app.py retrieve "How much printing credit does each student get per semester?"`.
Run `python -m unittest discover -s tests -v` for regression checks and
`python calibrate.py` to reproduce the distance table. See `RUNNING.md` for all commands.

**Implementation status:** the complete pipeline has been run with real local
embeddings and real Gemini responses. The environment check passes 10/10 and
regression tests pass 6/6. Five supported questions returned cited answers;
five out-of-scope questions were refused before generation. See
`results/unit1_answers.json` and `results/unit1_run.txt` for the captured outputs.
No stretch features are claimed. Criteria 4–5 were AI-assisted at the student's
request, after retrieval calibration; their authorship and timing are disclosed
in `criteria.md` rather than presented as student-written before implementation.

## Chunking Strategy

`chunker.py::split_documents` uses a **500-character soft body budget**, with
**0 characters of body overlap**. It packs complete paragraphs; a paragraph above
the budget is split at sentence boundaries. An individual overlong sentence is
kept whole, so 500 is deliberately not a hard maximum. A standalone post title
is repeated in each continuation chunk to identify its subject.

The source posts are short (about 317 characters on average). Keeping a short
post together preserves qualifications, prices and payment methods. Sliding-window
overlap would mostly duplicate these compact facts. The 500-character body target
keeps nearly all posts intact while separating the longest post into complete
paragraphs; title repetition supplies context without duplicating body text.
This plan was recorded in `BUILD_NOTES.md` before implementation.

Baseline: 88 documents, 88 chunks, mean 317 characters, range 178–549.
Custom chunker: 89 chunks, 314 characters on average (shortest 178, longest 516), produced by chunker.py::split_documents.
Only `housing_old_brewhouse.txt` splits into two chunks; its second chunk retains
the building title and the complete laundry/noise paragraph. The tradeoff is that
most short posts still contain several related facts. This is a documented design
choice, not a claim that these chunks are optimal.

## Sample Chunks

### Chunk 1

Source: `admin_add_drop_deadline.txt#0`. Produced by: `chunker.py::split_documents`.

```text
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

### Chunk 2

Source: `course_biol_160.txt#0`. Produced by: `chunker.py::split_documents`.

```text
BIOL 160 Cell Biology

I lived here my sophomore year. Format is lecture three times a week with a weekly lab. Assessment: four unit tests and a cumulative final. Not curved.

Expect 9 to 11 hours a week, the heaviest first-year course by reputation.

The one piece of advice: the unit tests come fast, roughly every three weeks; falling behind once is very hard to recover from.
```

### Chunk 3

Source: `course_hist_118_workload.txt#0`. Produced by: `chunker.py::split_documents`.

```text
Workload for HIST 118 Modern World History

People keep asking so: a lot of reading, about 120 pages a week, but no problem sets. That's real time, not optimistic time.

It's front-loaded — the first month is heavier than the rest, partly because you're learning the format.
```

### Chunk 4

Source: `dining_pellew_dining_hall_followup.txt#0`. Produced by: `chunker.py::split_documents`.

```text
Re: Pellew Dining Hall

Adding to what people have said about Pellew Dining Hall. The wait figure of 12 to 18 minutes at peak matches what I've seen. If you're trying to eat between classes, go before 11:45 and it's a different building entirely.

Also worth saying: the furthest hall from anywhere, next to the athletics centre. Nobody tells you this at orientation.
```

### Chunk 5

Source: `housing_innisfree_hall.txt#0`. Produced by: `chunker.py::split_documents`.

```text
Innisfree Hall — what it's actually like

Transferred in last year, so take this with a grain of salt. Built 1991, renovated 2022. Rooms are doubles arranged as pairs sharing one bathroom between two rooms.

The good: the shared-bathroom-between-two-rooms arrangement is the best compromise on campus.

The bad: no air conditioning, which matters for the first three weeks of September.

Laundry costs $1.75 wash, $1.75 dry, app-based. On noise: moderate; the building is L-shaped and the short wing is much quieter.
```

## Sample Answer

Question: How are juniors and seniors ranked in the housing lottery?

Answer (actual `gemini-3.5-flash-lite` response):

```text
Juniors and seniors are ordered by accumulated credit hours first, and only tie-break randomly (admin_housing_lottery.txt).

Sources: admin_housing_lottery.txt
```

The relevance gate passed with best distance 0.203422.
This sample and the other four in-scope answers were collected with response
caching disabled. Each in-scope question used one model call; all five unrelated
questions used zero calls and returned `I don't have enough information about that.`
Reproduce with `python verify_unit1.py` (makes five model calls).

### Relevance cutoff and measured distances

Cutoff: **0.60**, strict `<` comparison; top-k: **5**;
embedding model: **all-MiniLM-L6-v2**, real ONNX embeddings, cosine distance.

| Question | In corpus? | Best distance | Gate at 0.60 |
|---|---|---:|---|
| How are juniors and seniors ranked in the housing lottery? | Yes | 0.203422 | Pass |
| How much does a wash cost in Aldridge Hall, and how do you pay? | Yes | 0.273225 | Pass |
| What appears on my transcript if I drop a course after week two? | Yes | 0.267463 | Pass |
| How much printing credit does each student get per semester? | Yes | 0.376670 | Pass |
| What problem was reported on the ground floor of Morrow House? | Yes | 0.371654 | Pass |
| What is the capital of Mongolia? | No | 0.824593 | Refuse |
| How do I change the oil in a diesel engine? | No | 0.934011 | Refuse |
| Who won the 1994 World Cup? | No | 0.885860 | Refuse |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.844232 | Refuse |
| How do I write a for loop in Rust? | No | 0.895998 | Refuse |

The in-corpus distances range from 0.203422 to 0.376670; the out-of-corpus
distances range from 0.824593 to 0.934011. The midpoint between the closest
boundaries is about 0.601, so retaining 0.60 leaves a substantial margin on both
sides. All five supported questions pass and all five unrelated questions fail
on this calibration set. These are calibration observations, not an independent
Unit 2 evaluation or proof of performance on unseen questions. Near-topic unsupported
questions can still pass; the grounding prompt is the second line of defense.

`results/calibration.json` contains all five retrieved chunks and distances for
each of the ten questions, not just the best scores. All five in-scope questions
retrieve a chunk containing their expected phrase. The transcript expectation
`W` is a short keyword and still needs human checking in Unit 2 to avoid false positives.

The grounding instruction requires exact filenames for factual claims, a
`Sources:` line, preservation of qualifications, and refusal of unsupported
claims. It also treats document content as data rather than instructions.
In the captured run, all five substantive answers name existing source files
and the cited files support their factual claims. This is a single Unit 1 sanity
check, not the three-run Unit 2 assessment or a guarantee about later responses.

## How I Used AI

1. I provided the assignment PDF and asked Codex to help complete Project 1.
   Codex inspected the official starter and campus posts, drafted five test
   questions, and replaced fixed character windows with paragraph/sentence
   boundaries and repeated titles. The implementation changed the original
   800-character windows with 120-character overlap to a 500-character soft body
   budget with no body overlap. Codex added tests to check that source content
   survives splitting and that rejected questions never reach generation.
2. After configuring my Gemini key locally, I explicitly asked Codex to generate
   the acceptance targets. Codex drafted measurable chunk-quality and factual
   citation targets, recorded the AI authorship and timing, and then collected
   five real answers and five gate refusals. The measured distances supported
   keeping the starter's 0.60 cutoff; the sample-answer placeholder was replaced
   with actual output. I have not represented the AI-authored targets as my own
   independent pre-implementation work.
3. For Unit 2 I asked Codex to finish the evaluation. It ran the unchanged
   baseline, retained complete evidence, and reviewed the answers against source
   passages. It found a causal inference in the Morrow House answer, drafted one
   prompt rule, and ran the full after evaluation. The write-up reports that the
   error persisted in two of three after trials rather than claiming a full fix.
   The semantic scoring and diagnosis were AI-assisted; they are not presented
   as independently performed student judgments.

---

# Unit 2

## Run Log — Before

Baseline: Unit 1 commit `cf153db`, unchanged system. Evaluation on September 23,
2026, using `campus_life`, `all-MiniLM-L6-v2`, `gemini-3.5-flash-lite`, top-k 5,
and cutoff 0.60. The environment check passed 10/10. Criteria and questions were
not edited; their hashes are recorded in both evidence files. Unit 1's recorded
AI authorship and chronology remain visible in `criteria.md`.

The official evaluator ran all five questions three times with caching disabled.
The observation wrapper only saves returned chunks, request counts and sample
text; it does not change the pipeline or scoring rules. The three trials produced
15 real answers in **17 request attempts** (two rate-limit retries on Q5 run 3).
The repeats are real even when the model happens to return identical wording.

Commands:

```bash
source .venv/bin/activate
python test.py
python tools/unit2_capture.py --label before
```

`tools/unit2_capture.py` calls the unchanged `run_eval.py::main`, so the official
Markdown run log is produced too. It refuses to overwrite existing evidence;
for a new exploratory run use `python run_eval.py --label another-label`.

Evidence: [official before log](results/run_2026-09-23_1947_before.md),
[full returned chunks and answers](results/unit2_before_evidence.json),
[per-question judgments and source excerpts](results/unit2_before_review.md).
Scoring is AI-assisted reading of the actual output against source passages,
not substring matching: the expectation `W`, for example, is not accepted just
because that letter appears somewhere in a response. The raw evaluator's blank
score cells are expected because no scorer.py is installed.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every substantive answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunks preserve a complete, identifiable thought | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Every factual claim is supported by its citation | 4 of 5 | 4/5 | 4/5 | 4/5 | MET |

The target must hold in every run. C3 uses one deterministic evaluator pass,
repeated across columns as directed in the assignment. Additional full-pipeline
checks confirm the exact refusal and zero generation calls. C4's same five
samples were generated three separate times; deterministic identical results
are expected. C1, C2 and C5 are checked for each of all 15 answers/retrievals.

### Actual output supporting each criterion (before, run 1)

The following text is copied from `results/unit2_before_evidence.json`.
Retrieval is produced by `store.py::search`; answers by
`generate.py::answer_from_chunks`, called through `run_eval.py::run_once`.

**Criterion 1 — retrieved answer-bearing chunk**, source `admin_housing_lottery.txt`:

```text
On the housing lottery

The housing lottery is not random in the way most people assume. Rising sophomores get a number drawn at random, but juniors and seniors are ordered by accumulated credit hours first, and only tie-break randomly. That means a senior who took summer courses reliably beats a senior who didn't. Numbers come out the second week of March and selection runs over four evenings.
```

**Criterion 2 — the actual answer names a source**:

```text
Juniors and seniors are ordered by accumulated credit hours first, and only tie-break randomly (admin_housing_lottery.txt).

Sources: admin_housing_lottery.txt
```

**Criterion 3 — actual application refusal**, produced by
`app.py::ask_pipeline` and `gate.py::check`:

```text
Question: What is the capital of Mongolia?
I don't have enough information about that.
```

Recorded fields: `refused=true`, `generation_calls=0`.

**Criterion 4 — actual sampled chunk**, source `admin_add_drop_deadline.txt`, produced by
`chunker.py::split_documents`:

```text
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Criterion 5 — actual Morrow House answer**:

```text
A known damp problem was reported on the ground floor of Morrow House, which resulted in two rooms being taken offline in 2024.

Sources: housing_morrow_house.txt
```

The source says: `The bad: known damp problem on the ground floor; two rooms were taken offline in 2024.`
The words "which resulted in" are an added causal claim, not an explicit source
statement. This answer fails criterion 5's per-answer check even though the
aggregate criterion meets its four-of-five target.

## Verdicts

| Criterion | Verdict | How I decided |
|---|---|---|
| 1. Retrieval | MET | Each of five questions has a retrieved chunk supplying all requested facts in every run. Laundry includes both price and payment method. |
| 2. Citation present | MET | Every generated answer contains an existing source filename, including its model-written Sources line; I did not count the CLI's separate list. |
| 3. Gate | MET | All five unrelated questions are refused with the exact gate.REFUSAL string and no generation call; 5/5 exceeds 4/5. |
| 4. Chunk quality | MET | All five samples identify their subject, contain a factual statement, and have no splitting-induced sentence fragment in all three samples. |
| 5. Claim support | MET | Q1–Q4 pass and Q5 fails in all three baseline runs, giving exactly 4/5 each time. MET does not mean every answer is correct. |

The detailed per-question and per-chunk checklists are in
[the baseline review](results/unit2_before_review.md). No criterion was rewritten
or lowered. The strict causal-support judgment applies identically before and
after. Under a looser interpretation of the source's semicolon the Morrow answer
might be accepted; this review follows the existing requirement of explicit
support or direct entailment, rather than treating a plausible inference as fact.

## Diagnoses

**No aggregate criterion was missed.** However, Q5 failed the factual-support
check three times. Stage: **generation**. Mechanism: two adjacent observations
in a correctly retrieved chunk were joined with "which resulted in," inventing
a causal connection. Loading retained the sentence, chunking kept it whole,
and retrieval selected the correct document; the error arose in the answer.

Unit 1's informal statement that every answer was supported was too generous:
this more explicit claim-by-claim review identifies an unsupported causal link.
The Unit 1 record is retained rather than rewritten to imply it was caught then.

The original C5 target is permissive: 4/5 allows the same question to hallucinate
in every run. C1 asks only for one useful chunk among five, C3 uses very distant
topics, and C4 samples only five of 89 chunks. Passing this small set is not proof
of general reliability. In future I would tighten C5 to 5/5 per run and use held-out
questions, including nearby but unsupported campus questions; those are proposals,
not changes to this evaluation's targets or question set.

## The Improvement

**What I changed:** one additional rule in
`generate.py::GROUNDING_INSTRUCTION`:

```text
Do not turn adjacent observations into a causal claim. State causation only when the source explicitly connects cause and effect; otherwise report the observations separately without causal language.
```

**Why I picked it:** the correct source is already retrieved, but generation
converts association into causation. This rule targets that mechanism directly.
The diagnosis and prediction were committed before the prompt edit, and the edit
was committed before the after evaluation. No second improvement or stretch
feature was attempted.

Only this one prompt rule changed the system. Corpus, chunking, models, top-k,
cutoff, criteria, questions and evaluator remain unchanged. The two evidence
files contain exactly matching retrieved text and distances for all 15 entries,
as well as matching chunk samples and criteria/question hashes.

### Run Log — After

```bash
python tools/unit2_capture.py --label after
```

This produced 15 fresh answers in 15 request attempts, with caching disabled,
and repeated the full gate and chunk checks. Evidence:
[official after log](results/run_2026-09-23_1949_after.md),
[full after evidence](results/unit2_after_evidence.json), and
[paired per-question scoring ledger](results/unit2_after_review.md).

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every substantive answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunks preserve a complete, identifiable thought | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Every factual claim is supported by its citation | 4 of 5 | 4/5 | 4/5 | 5/5 | MET |

### Actual output supporting each criterion (after, run 1)

The following text is copied from `results/unit2_after_evidence.json`.
Retrieval is produced by `store.py::search`; answers by
`generate.py::answer_from_chunks`, called through `run_eval.py::run_once`.

**Criterion 1 — retrieved answer-bearing chunk**, source `admin_housing_lottery.txt`:

```text
On the housing lottery

The housing lottery is not random in the way most people assume. Rising sophomores get a number drawn at random, but juniors and seniors are ordered by accumulated credit hours first, and only tie-break randomly. That means a senior who took summer courses reliably beats a senior who didn't. Numbers come out the second week of March and selection runs over four evenings.
```

**Criterion 2 — the actual answer names a source**:

```text
Juniors and seniors are ordered by accumulated credit hours first, and only tie-break randomly (admin_housing_lottery.txt).

Sources: admin_housing_lottery.txt
```

**Criterion 3 — actual application refusal**, produced by
`app.py::ask_pipeline` and `gate.py::check`:

```text
Question: What is the capital of Mongolia?
I don't have enough information about that.
```

Recorded fields: `refused=true`, `generation_calls=0`.

**Criterion 4 — actual sampled chunk**, source `admin_add_drop_deadline.txt`, produced by
`chunker.py::split_documents`:

```text
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Criterion 5 — actual Morrow House answer**:

```text
A known damp problem was reported on the ground floor of Morrow House, which resulted in two rooms being taken offline in 2024 (housing_morrow_house.txt).

Sources: housing_morrow_house.txt
```

The source says: `The bad: known damp problem on the ground floor; two rooms were taken offline in 2024.`
The words "which resulted in" are an added causal claim, not an explicit source
statement. This answer fails criterion 5's per-answer check even though the
aggregate criterion meets its four-of-five target.

### Before/after comparison

| Measure | Before | After |
|---|---|---|
| C1 answer-bearing retrieval, runs 1/2/3 | 5/5, 5/5, 5/5 | 5/5, 5/5, 5/5 |
| C2 cited answers, runs 1/2/3 | 5/5, 5/5, 5/5 | 5/5, 5/5, 5/5 |
| C3 deterministic refusals | 5/5 | 5/5 |
| C4 complete sample chunks, runs 1/2/3 | 5/5, 5/5, 5/5 | 5/5, 5/5, 5/5 |
| C5 fully supported answers, runs 1/2/3 | 4/5, 4/5, 4/5 | 4/5, 4/5, 5/5 |
| Q5 unsupported causal answers | 3/3 | 2/3 |

Actual Q5 after-run-3 output, produced by `generate.py::answer_from_chunks`:

```text
A known damp problem on the ground floor was reported in Morrow House (housing_morrow_house.txt).

Sources: housing_morrow_house.txt
```

**Did it help?** The observed number of fully supported answers increased from
12/15 to 13/15, but the unsupported claim still appeared in two of three Q5
answers. All five aggregate verdicts remained MET. This is a limited observed
improvement, not a reliable fix or statistically persuasive proof that the prompt
caused the change; a single response could differ through model randomness.

## What's Still Broken

No aggregate target is missed after the change, but the cause-and-effect
hallucination remains in Q5 runs 1 and 2. A prompt instruction is not a hard
constraint. A next investigation would test claim-level support verification
or a more extractive answer format on separate held-out cases before adopting
another change. I stopped after the one planned intervention and full after
measurement to preserve an interpretable comparison; I did not keep editing or
rerunning until an attractive result appeared.

The five questions are narrow and the out-of-scope set is easy. Nearby questions
with missing details may pass the gate. Source anecdotes can also be inaccurate,
and citations only establish consistency with the provided corpus, not real-world
truth. The BIOL post's awkward "I lived here" opening illustrates imperfect source
text; passing C4 does not certify the source's quality. Those limits were not
addressed by this improvement.

## What I'd Do Differently

For a future project I would require C5 to pass 5/5 in every run and assess more
than five questions, including claims involving dates, prices, causal language,
negation and uncertainty. I would define an explicit example of unsupported
causation before scoring to reduce judgment ambiguity. I would sample split
continuations for C4 and add near-domain missing-information questions for C3.
These are future designs, not replacements for the preserved Unit 1 targets.
I would also author and commit my own criteria before implementation and
calibration; the existing AI-assisted timing remains disclosed in criteria.md.

The existing six regression tests pass after the prompt edit
([test output](results/unit2_regression_tests.txt)). They protect chunk handling
and gate control flow; they do not establish semantic correctness of generated
answers. Both actual run logs and the detailed review evidence are committed.
