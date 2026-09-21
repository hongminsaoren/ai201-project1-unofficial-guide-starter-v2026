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


---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
