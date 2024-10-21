import unittest
from cloze import get_regex_patterns, get_clozed_sentence

class TestCloze(unittest.TestCase):
    
    def test_normal_target_words(self):
        regex_patterns = get_regex_patterns(['some', 'any', 'no'])
        clozed_sentences = []
        sentences = ['Some people are so rude.',
                     'I don\'t have any time for anything.',
                     'Sometimes I have trouble saying no.',
                     'No one had any questions, so I gave them some exercises.']
        for sentence in sentences:
            clozed_sentence = get_clozed_sentence(sentence, regex_patterns)[0]
            clozed_sentences.append(clozed_sentence)
        sentences_to_compare = ['____ people are so rude.',
                                'I don\'t have ____ time for anything.',
                                'Sometimes I have trouble saying ____.',
                                '____ one had ____ questions, so I gave them ____ exercises.']
        for i, sentence in enumerate(sentences_to_compare):
            with self.subTest(sentence):
                clozed_sentence = clozed_sentences[i]
                message = f'Expected "{sentence}".'
                self.assertEqual(sentence, clozed_sentence, message)
    
    def test_partial_target_words(self):
        regex_patterns = get_regex_patterns(['some...', 'any...', 'no...'])
        clozed_sentences = []
        sentences = ['Sometimes some people are so rude.',
                     'I don\'t have any time for anything.',
                     'Sometimes I have trouble saying no.',
                     'Nobody had any questions, so I gave them some exercises.']
        for sentence in sentences:
            clozed_sentence = get_clozed_sentence(sentence, regex_patterns)[0]
            clozed_sentences.append(clozed_sentence)
        sentences_to_compare = ['____times some people are so rude.',
                                'I don\'t have any time for ____thing.',
                                '____times I have trouble saying no.',
                                '____body had any questions, so I gave them some exercises.']
        for i, sentence in enumerate(sentences_to_compare):
            with self.subTest(sentence):
                clozed_sentence = clozed_sentences[i]
                message = f'Expected "{sentence}".'
                self.assertEqual(sentence, clozed_sentence, message)
                
    def test_parenthetical_target_words(self):
        regex_patterns = get_regex_patterns(['some(thing)', 
                                             'some(body)',
                                             'any(thing)',
                                             'any(body)',
                                             'no(thing)',
                                             'no(body)'])
        clozed_sentences = []
        sentences = ['You can\'t get something from nothing.',
                     'I don\'t have any time for anything.',
                     'I usually want to do something, but not when it\'s raining.',
                     'Nobody had any questions, so I gave them some exercises.']
        for sentence in sentences:
            clozed_sentence = get_clozed_sentence(sentence, regex_patterns)[0]
            clozed_sentences.append(clozed_sentence)
        sentences_to_compare = ['You can\'t get ____thing from ____thing.',
                                'I don\'t have any time for ____thing.',
                                'I usually want to do ____thing, but not when it\'s raining.',
                                '____body had any questions, so I gave them some exercises.']
        for i, sentence in enumerate(sentences_to_compare):
            with self.subTest(sentence):
                clozed_sentence = clozed_sentences[i]
                message = f'Expected "{sentence}".'
                self.assertEqual(sentence, clozed_sentence, message)

unittest.main()
            