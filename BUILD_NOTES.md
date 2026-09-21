# Unit 1 implementation log

## Setup and corpus decision

The official starter history is preserved, and `origin` points to the student's
fork. Work uses `campus_life`: the supplied fictional campus posts, not factual
advice about UC Berkeley or another real university. Housing, deadlines and
printing posts have been read before selecting the test questions.

Dependencies are installed in `.venv`; the API key belongs only in ignored `.env`.
At this initial checkpoint, generation had not been verified because a key was not yet configured.
This is a setup checkpoint, not a claim that Milestone 1 has passed end to end.

## Proposed chunking, before implementation or retrieval measurements

Use 500 characters as a soft body budget, preserve paragraph boundaries, and
split oversized paragraphs only at sentence boundaries. Carry the original
post title into each chunk so a continuation still identifies the building or
policy it describes. Most posts should remain whole; longer multi-paragraph
posts can separate without losing their subject. A sentence longer than the
budget stays intact rather than being truncated.

Body overlap: zero characters. These short posts already contain compact facts;
repeating a previous paragraph would duplicate unrelated topics. The title is
repeated contextual metadata, not sliding-window overlap. Top-k starts at 5.

## Student-owned work

The assignment asks the student to author criteria 4 and 5 and the rationale
for all five criteria. At this initial checkpoint those were pending. The later update below records
the student's instruction and the actual authorship; it does not backdate them.

## Starter observation

Before replacing the chunker, the required advice_threads command reported
**26** chunks total. Test questions and expected phrases were selected directly
from source documents, before retrieving answers to those five questions.

## Follow-up: real answers and criteria draft

The student confirmed local API-key configuration and explicitly asked Codex to
write the acceptance targets. Criteria 4–5 and all rationales were committed as
an AI-assisted draft after calibration, before hosted answer validation.
This differs from the assignment's requested student-authored chronology and is
openly disclosed in criteria.md. Earlier commits and measurements are preserved.

The official environment check then passed all 10 checks, including a real model
call. `verify_unit1.py` captured one fresh answer for each of five in-scope
questions and confirmed five gate refusals with zero generation calls. All five
answers cite source files supporting their content. This is Unit 1 verification;
Unit 2's repeated evaluation has not been run or filled in.
