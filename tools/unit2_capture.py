"""Run the unchanged evaluator and retain extra evidence; never score by keyword.

Usage: python tools/unit2_capture.py --label before
The wrapper records the exact chunks returned by each real run, call counts,
token deltas, and deterministic chunk samples. It does not alter retrieval,
prompts, questions, criteria, or evaluator caching (which stays disabled).
"""
import dataclasses
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import config
import generate
import run_eval
from app import ask_pipeline
from chunker import split_documents
from ingest import load_documents

label = sys.argv[sys.argv.index('--label') + 1]
if label not in {'before', 'after'}:
    raise SystemExit('Use --label before or --label after')
path = ROOT / 'results' / f'unit2_{label}_evidence.json'
if path.exists():
    raise SystemExit(f'Refusing to overwrite {path}; preserve prior evidence.')
evidence = {
    'label': label,
    'started_at': datetime.datetime.now().astimezone().isoformat(),
    'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'model': config.MODEL, 'embedding_model': config.EMBEDDING_MODEL,
    'corpus': config.CORPUS, 'top_k': config.TOP_K, 'threshold': config.THRESHOLD,
    'criteria_sha256': hashlib.sha256((ROOT / 'criteria.md').read_bytes()).hexdigest(),
    'questions_sha256': hashlib.sha256((ROOT / 'questions.py').read_bytes()).hexdigest(),
    'cache': False, 'answers': [], 'gate_pipeline': [], 'chunk_samples': [],
}


def save():
    path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + '\n')


original = run_eval.run_once


def capture(*args, **kwargs):
    calls = generate.call_count()
    tokens = generate.token_counts()
    answer, results, decision = original(*args, **kwargs)
    evidence['answers'].append({
        'question': args[0], 'answer': answer,
        'results': [dataclasses.asdict(r) for r in results],
        'gate': dataclasses.asdict(decision),
        'generation_calls': generate.call_count() - calls,
        'tokens': {k: v - tokens[k] for k, v in generate.token_counts().items()},
    })
    save()
    return answer, results, decision


run_eval.run_once = capture
save()
run_eval.main()
# Capture the full application refusal, not just the evaluator's gate decision.
for question in run_eval.qs.OUT_OF_SCOPE:
    calls = generate.call_count()
    result = ask_pipeline(question)
    evidence['gate_pipeline'].append({**result, 'generation_calls': generate.call_count() - calls})
    save()
# Repeat the five deterministic samples three times, with no code changes.
for _ in range(3):
    chunks = split_documents(load_documents())
    sample = chunks[::max(len(chunks) // 5, 1)][:5]
    evidence['chunk_samples'].append([dataclasses.asdict(c) for c in sample])
evidence['completed_at'] = datetime.datetime.now().astimezone().isoformat()
save()
print(f'Additional evidence: {path.relative_to(ROOT)}')
