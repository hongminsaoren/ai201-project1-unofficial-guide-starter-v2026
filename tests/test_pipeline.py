import unittest
from unittest.mock import patch

import config
from chunker import split_documents
from ingest import Document, load_documents
from store import Result
import gate
from app import ask_pipeline


class ChunkTests(unittest.TestCase):
    def test_corpus_content_and_source_preserved(self):
        for doc in load_documents('campus_life'):
            chunks = split_documents([doc])
            self.assertTrue(chunks)
            self.assertEqual([c.index for c in chunks], list(range(len(chunks))))
            self.assertTrue(all(c.source == doc.source for c in chunks))
            title, _, body = doc.text.partition('\n\n')
            reconstructed = ' '.join(c.text.removeprefix(title).strip() for c in chunks)
            self.assertEqual(' '.join(body.split()), ' '.join(reconstructed.split()))

    def test_long_paragraph_preserves_sentences_and_title(self):
        sentences = ['Alpha has useful context.', 'Beta has more details.', 'Gamma explains the exception.']
        with patch.object(config, 'CHUNK_SIZE', 40):
            chunks = split_documents([Document('a.txt', 'Campus example\n\n' + ' '.join(sentences))])
        self.assertEqual(len(chunks), 3)
        for chunk, sentence in zip(chunks, sentences):
            self.assertEqual(chunk.text, 'Campus example\n\n' + sentence)

    def test_long_sentence_is_not_truncated(self):
        sentence = 'A ' + 'long ' * 120 + 'sentence.'
        chunks = split_documents([Document('long.txt', sentence)])
        self.assertEqual([c.text for c in chunks], [sentence])

    def test_empty_document(self):
        self.assertEqual(split_documents([Document('empty.txt', ' \n\n ')]), [])


class GateTests(unittest.TestCase):
    def test_rejection_never_calls_generator(self):
        for results in ([], [Result('unrelated', 'a.txt', 'a.txt#0', .9, 'test')]):
            with patch('store.search', return_value=results), patch('generate.answer_from_chunks') as generate:
                outcome = ask_pipeline('an unrelated question')
                self.assertTrue(outcome['refused'])
                self.assertEqual(outcome['answer'], gate.REFUSAL)
                generate.assert_not_called()

    def test_strict_boundary(self):
        result = Result('text', 'a.txt', 'a.txt#0', .6, 'test')
        self.assertFalse(gate.check([result], threshold=.6).passed)
        self.assertTrue(gate.check([result], threshold=.61).passed)


if __name__ == '__main__':
    unittest.main()
