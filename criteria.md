# Acceptance criteria — The Unofficial Guide

Criteria 1–3 are the assignment's supplied targets. Criteria 4–5 and the
rationales below were drafted by Codex at the student's explicit request.
These additions were recorded after Unit 1 retrieval calibration and chunk
implementation, but before collecting the first hosted sample answer or running
the Unit 2 evaluation. They must not be represented as student-authored,
pre-implementation criteria. The assignment asks for student-authored criteria;
this AI-assisted draft does not meet that authorship instruction as written.
Keep this history and disclose any later revisions rather than backdating them.

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**How to check:** Run all five questions in `questions.py` with the default
`TOP_K = 5`. Read each retrieved chunk against the question; a keyword alone is
not sufficient. Count a success only if one chunk supplies all requested facts.

**Why this target:** Several housing posts reuse laundry and noise vocabulary,
so a neighboring building can be a plausible retrieval mistake. Four of five
requires useful retrieval across housing and administrative topics while allowing
one such miss; three would leave too many everyday questions unanswered.

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**How to check:** For each substantive answer to the five test questions, check
that at least one exact filename in `corpora/campus_life/documents/` appears in
the answer text. Gate refusals are evaluated under criterion 3 and do not invent
citations. A sources list printed separately by the CLI does not excuse an
uncited answer body.

**Why this target:** Filenames are already provided to the model with every
excerpt. Every substantive answer should therefore be traceable, including a
partially supported answer; accepting four of five would knowingly leave one
answer without a way to verify its claims.

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

**How to check:** Use the five distinct questions in `OUT_OF_SCOPE`, once each.
Require `refused` to be true, the response to equal `gate.REFUSAL` (including its
trailing period), and no generation call for that question. A refusal produced
by the model after the gate passes does not count as a gate success.

**Why this target:** The corpus covers campus life rather than world history,
vehicle maintenance, medicine or programming. The supplied four-of-five target
allows one misleading semantic match but still requires reliable refusal;
calibration currently separates these groups, which is evidence for the cutoff,
not a reason to lower the target later.

## 4. Sample chunks preserve a usable, complete thought

At least 4 of the 5 chunks selected by `python app.py chunks -n 5` must identify
their subject in the chunk text, contain at least one complete factual statement,
and neither begin nor end with a sentence fragment introduced by splitting.
All three conditions must hold for a sampled chunk to count.

**How to check:** Compare each displayed chunk with its source document. Record
three yes/no judgments for each chunk: subject identifiable without a neighboring
chunk, complete factual statement present, and no sentence cut at either edge.
Only a row with three yes judgments passes.

**Why this target:** Campus posts often use pronouns such as "here" and "this
building," so intact punctuation alone does not make a chunk useful. Requiring
four complete, self-contained samples checks both boundaries and context, while
allowing one informal source post to be ambiguous. Requiring only three would
leave almost half of the sample unusable on its own.

## 5. Cited answers support every factual claim

For at least 4 of the 5 in-corpus test questions, the system must produce a
substantive answer in which every factual claim is supported by the exact source
file cited for that claim, without adding prices, deadlines, rules or other facts
that are absent from that source. A refusal does not count as a success.

**How to check:** Break each answer into factual claims and open the filename
cited for each claim. Mark a claim supported only when that file explicitly
states it or directly entails it. Missing, nonexistent or unrelated citations
fail the answer, as does any unsupported claim. Record evidence passages so
another reader can check the judgment.

**Why this target:** A filename can be present while the model mixes the price
or policy from another building. Four fully supported answers out of five is a
stronger requirement than merely printing citations, while allowing one failure
to diagnose in Unit 2. Student anecdotes must remain anecdotes rather than being
silently upgraded to official university policy.

## Unit 2 revision policy

Preserve these targets. If a criterion cannot be measured, append a dated
revision and explain the ambiguity; do not erase the original or lower a target
because the system missed it. Unit 1 calibration is not a held-out evaluation.
