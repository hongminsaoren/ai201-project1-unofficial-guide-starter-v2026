"""Capture actual Unit 1 answers and gate decisions; not the Unit 2 scorer."""
import json
from pathlib import Path
from unittest.mock import patch

import config
from app import ask_pipeline
from generate import call_count
from questions import QUESTIONS, OUT_OF_SCOPE


def main():
    records = []
    for question in QUESTIONS:
        before = call_count()
        result = ask_pipeline(question['question'])
        result['generation_calls'] = call_count() - before
        records.append(result)
        print(question['question'], flush=True)
        print(result['answer'], flush=True)
    for question in OUT_OF_SCOPE:
        before = call_count()
        result = ask_pipeline(question)
        result['generation_calls'] = call_count() - before
        assert result['refused'], question
        assert result['generation_calls'] == 0, question
        records.append(result)
        print(f"REFUSED ({result['generation_calls']} model calls): {question}", flush=True)
    Path('results/unit1_answers.json').write_text(json.dumps({
        'model': config.MODEL, 'threshold': config.THRESHOLD,
        'note': 'One actual run per question; this is not the Unit 2 repeated evaluation.',
        'records': records,
    }, indent=2) + '\n')


if __name__ == '__main__':
    # Always collect fresh answers rather than return a prior response cache.
    with patch.object(config, 'CACHE_ENABLED', False):
        main()
