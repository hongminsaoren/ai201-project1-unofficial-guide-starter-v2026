# Unit 1 implementation log

## Setup and corpus decision

The official starter history is preserved, and `origin` points to the student's
fork. Work uses `campus_life`: the supplied fictional campus posts, not factual
advice about UC Berkeley or another real university. Housing, deadlines and
printing posts have been read before selecting the test questions.

Dependencies are installed in `.venv`; the API key belongs only in ignored `.env`.
Generation has not yet been verified because the student must configure a key.
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
for all five criteria. Those remain pending; AI must not be described as having
received or validated criteria the student has not supplied. Do not claim a
complete submission until these and a real generated sample answer are present.

## Starter observation

Before replacing the chunker, the required advice_threads command reported
**26** chunks total. Test questions and expected phrases were selected directly
from source documents, before retrieving answers to those five questions.
