import pyinflect
import random
from models import Error, Correction



glossary = {
    # Universal POS Tags
    # http://universaldependencies.org/u/pos/
    "ADJ": "adjective",
    "ADP": "adposition",
    "ADV": "adverb",
    "AUX": "auxiliary",
    "CONJ": "conjunction",
    "CCONJ": "coordinating conjunction",
    "DET": "determiner",
    "INTJ": "interjection",
    "NOUN": "noun",
    "NUM": "numeral",
    "PART": "particle",
    "PRON": "pronoun",
    "PROPN": "proper noun",
    "PUNCT": "punctuation",
    "SCONJ": "subordinating conjunction",
    "SYM": "symbol",
    "VERB": "verb",
    "X": "other",
    "EOL": "end of line",
    "SPACE": "space",
    # POS tags (English)
    # OntoNotes 5 / Penn Treebank
    # https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
    ".": "punctuation mark, sentence closer",
    ",": "punctuation mark, comma",
    "-LRB-": "left round bracket",
    "-RRB-": "right round bracket",
    "``": "opening quotation mark",
    '""': "closing quotation mark",
    "''": "closing quotation mark",
    ":": "punctuation mark, colon or ellipsis",
    "$": "symbol, currency",
    "#": "symbol, number sign",
    "AFX": "affix",
    "CC": "conjunction, coordinating",
    "CD": "cardinal number",
    "DT": "determiner",
    "EX": "existential there",
    "FW": "foreign word",
    "HYPH": "punctuation mark, hyphen",
    "IN": "conjunction, subordinating or preposition",
    "JJ": "adjective",
    "JJR": "adjective, comparative",
    "JJS": "adjective, superlative",
    "LS": "list item marker",
    "MD": "verb, modal auxiliary",
    "NIL": "missing tag",
    "NN": "noun, singular or mass",
    "NNP": "noun, proper singular",
    "NNPS": "noun, proper plural",
    "NNS": "noun, plural",
    "PDT": "predeterminer",
    "POS": "possessive ending",
    "PRP": "pronoun, personal",
    "PRP$": "pronoun, possessive",
    "RB": "adverb",
    "RBR": "adverb, comparative",
    "RBS": "adverb, superlative",
    "RP": "adverb, particle",
    "TO": 'infinitival "to"',
    "UH": "interjection",
    "VB": "verb, base form",
    "VBD": "verb, past tense",
    "VBG": "verb, gerund or present participle",
    "VBN": "verb, past participle",
    "VBP": "verb, non-3rd person singular present",
    "VBZ": "verb, 3rd person singular present",
    "WDT": "wh-determiner",
    "WP": "wh-pronoun, personal",
    "WP$": "wh-pronoun, possessive",
    "WRB": "wh-adverb",
    "SP": "space",
    "ADD": "email",
    "NFP": "superfluous punctuation",
    "GW": "additional word in multi-word expression",
    "XX": "unknown",
    "BES": 'auxiliary "be"',
    "HVS": 'forms of "have"',
    "_SP": "whitespace"}


#def explain_pos_tag(tag):
#    if tag in glossary:
#        return glossary[tag].upper()
#    else:
#        return "Not found"
    

def get_word_forms(parsed_sentence):
    sentence_list = []
    for token in parsed_sentence:
        inflected_forms = [token.lower_]
        if token.tag_.startswith('V'):
            if token.lemma_ == 'be':
                inflected_forms = ['be', 'am', 'is', 'are',
                                   'was', 'were', 'been', 'being']
            else:
                for pos in ["VBP", "VBD", "VBG", "VBN", "VBZ"]:
                    inflected_form = token._.inflect(pos)
                    print(inflected_form)
                    if inflected_form and inflected_form not in inflected_forms:
                        inflected_forms.append(inflected_form.lower())
        elif token.tag_.startswith('J'):
            for pos in ["JJ", "JJR", "JJS"]:
                inflected_form = token._.inflect(pos)
                print(inflected_form)
                if inflected_form and inflected_form not in inflected_forms:
                    inflected_forms.append(inflected_form.lower())
        elif token.tag_ == 'NN':
            inflected_form = token._.inflect('NNS')
            print(inflected_form)
            if inflected_form and inflected_form not in inflected_forms:
                inflected_forms.append(inflected_form.lower()) 
        sentence_list.append(inflected_forms)
        print(inflected_forms)
    print(sentence_list)
    return sentence_list


def get_verb_form_list(verb_forms, num_sentences):
    import spacy
    nlp = spacy.load('en_core_web_sm')
    
    all_errors = Error.query.all()
    num_errors = len(all_errors)
    seen_sentences = []
    verb_form_list = []
    if verb_forms == 'gerund_infinitive':
        target_pos_tags = ['VBG', 'TO', 'VB']
    elif verb_forms == 'subject_verb':
        target_pos_tags = ['VBP', 'VBZ']
    else:
        target_pos_tags = ['VBP', 'VBZ', 'VBD', 'VBN', 'VBG']
    
    while len(verb_form_list) < num_sentences:
        random_error = Error.query.filter_by(id = random.choice(range(num_errors))).first()
        if random_error:
            sentence = random_error.corrections[0].correct_sentence
            parsed_sentence = nlp(sentence)
            word_list = []
            if sentence not in seen_sentences:
                for token in parsed_sentence:
                    next = parsed_sentence[token.i+1] if token.i+1 < len(parsed_sentence) else None
                    prev = parsed_sentence[token.i-1] if token.i-1 >= 0 else None
                    #Punctuation:
                    if next and next.is_punct:
                        if next.text == '-' and parsed_sentence[next.i+1]:
                            word_list_item = [token.text + next.text + parsed_sentence[next.i+1].text]
                        else:
                            word_list_item = [token.text + next.text]
                    elif token.is_punct and word_list and len(word_list[-1]) < 2:
                        continue
                    elif prev and prev.text == '-':
                        continue
                    
                    #Gerunds and Infinitives:
                    elif token.tag_ == 'TO' and verb_forms == 'gerund_infinitive':
                        if next and next.tag_ == 'VB' and prev and prev.lemma_ not in [
                                                            'be', 'like', 'love', 'prefer', 'continue', 'start'
                                                            ] and prev.text != 'n\'t':
                            continue
                        else:
                            word_list_item = [token.text]
                    elif token.tag_ == 'VB' and verb_forms == 'gerund_infinitive' and (prev and prev.tag_ == 'MD') or\
                                (prev and prev.tag_ == 'PRP' and parsed_sentence[prev.i-1] and parsed_sentence[prev.i-1].lemma_ in ['let', 'make', 'help']):
                        word_list_item = [token.text] + get_verb_forms(token, target_pos_tags)
                    elif token.tag_ == 'VB' and verb_forms == 'gerund_infinitive':
                        if prev and prev.tag_ == 'TO' and word_list and word_list[-1][0] != 'to':
                            word_list_item = ['to ' + token.text] + get_verb_forms(token, target_pos_tags)
                        else:
                            word_list_item = [token.lower_]
                    elif token.tag_ == 'VBG' and verb_forms == 'gerund_infinitive':
                        if prev and (prev.lemma_ in [
                            'be', 'like', 'love', 'prefer', 'continue', 'start'
                            ] or prev and prev.text == 'n\'t'):
                            word_list_item = [token.text]
                        else:
                            word_list_item = [token.text] + get_verb_forms(token, target_pos_tags)
                    
                    #Subject-Verb Agreement:
                    elif (token.tag_ == 'VBZ' or token.tag_ == 'VBP') and verb_forms == 'subject_verb':
                        if (token.text in ['am', '\'m']) or (prev and prev.lower_ in ['i', 'you']) or\
                            (token.lemma_ == 'be' and prev and prev.lower_ in ['he', 'she', 'it']):
                            word_list_item = [token.text]
                        elif next and next.text == 'n\'t':
                            word_list_item = [token.text + 'n\'t'] + get_verb_forms(token, target_pos_tags, 'n\'t')
                        else:
                            word_list_item = [token.text] + get_verb_forms(token, target_pos_tags)
                    elif next and next.text.startswith('\''):
                        if (next.tag_ == 'VBZ' or next.tag_ == 'VBP') and verb_forms == 'subject_verb':
                            word_list_item = [token.text]
                        else:
                            word_list_item = [token.text + next.text]
                    elif token.text.startswith('\''):
                        if (token.tag_ == 'VBZ' or token.tag_ == 'VBP') and verb_forms == 'subject_verb':
                            word_list_item = [token.text] + get_verb_forms(token, target_pos_tags)
                        else:
                            continue
                    
                    #All verb forms:
                    elif token.pos_ == 'VERB' and token.lemma_ != 'be' and verb_forms == 'all_forms':
                        if (next and next.text == 'n\'t') or token.text.startswith('\''):
                            word_list_item = [token.text + 'n\'t']
                        else:
                            word_list_item = [token. text] + get_verb_forms(token, target_pos_tags)

                    elif next and next.text == 'n\'t':
                        word_list_item = [token.text + 'n\'t']
                    elif token.text == 'n\'t':
                        continue                            
                    else:
                        word_list_item = [token.text]
                    word_list.append(word_list_item)
                
                for word in word_list:
                    if len(word) > 1 and sentence not in seen_sentences:
                        for i, option in enumerate(word_list[0]):
                            word_list[0][i] = option.capitalize()
                        sentence_dict = {'word_list': word_list,
                                         'error_id': random_error.id,
                                         'correct_answers_needed': 3}
                        verb_form_list.append(sentence_dict)
                        seen_sentences.append(sentence)
                        break
            
    return verb_form_list


                            
def get_verb_forms(token, target_pos_tags, contraction=None):
    inflected_forms = []
    inflected_form = None
    contraction = contraction if contraction else ''
    for pos in target_pos_tags:
        if pos == 'TO':
            infinitive = token._.inflect('VB')
            if infinitive:
                inflected_form = 'to ' + infinitive
        else:
            if token.lemma_ == 'be' and (token.tag_ == 'VBP' or token.tag_ == 'VBZ'):
                if token.text.startswith('\''):
                    inflected_forms += ['\'re', '\'s']
                    break
                else:
                    inflected_forms += ['are' + contraction, 'is' + contraction]
                    break
            elif token.lemma_ == 'have' and (token.tag_ == 'VBP' or token.tag_ == 'VBZ') and\
                                             token.text.startswith('\''):
                inflected_forms += ['\'ve', '\'s']
                break
            elif token.lemma_ == 'work' and pos in ['VBD', 'VBN']:
                inflected_form = 'worked'
            elif token.lemma_ == 'learn' and pos in ['VBD', 'VBN']:
                inflected_form = 'learnt'
            else:
                existing_inflected_form = token._.inflect(pos)
                if existing_inflected_form:
                    inflected_form = token._.inflect(pos) + contraction
        if inflected_form and inflected_form.lower() not in inflected_forms:
            inflected_forms.append(inflected_form.lower())
    return inflected_forms