"""Measure the ten predefined questions without making any hosted model calls."""
import json
from dataclasses import asdict
from pathlib import Path
import config
from questions import QUESTIONS, OUT_OF_SCOPE
from store import search


def main():
    rows = []
    for covered, questions in [(True, [q['question'] for q in QUESTIONS]), (False, OUT_OF_SCOPE)]:
        for question in questions:
            results = search(question, top_k=config.TOP_K)
            row = {'question': question, 'in_corpus': covered,
                   'best_distance': min((r.distance for r in results), default=1.0),
                   'results': [asdict(r) for r in results]}
            rows.append(row)
            print(f"{'IN ' if covered else 'OUT'} {row['best_distance']:.6f} {question}")
    payload = {'corpus': config.CORPUS, 'embedding_model': config.EMBEDDING_MODEL,
               'top_k': config.TOP_K, 'rows': rows}
    Path('results/calibration.json').write_text(json.dumps(payload, indent=2)+'\n')


if __name__ == '__main__':
    main()
