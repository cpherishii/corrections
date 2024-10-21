from app import current_user
from extensions import db
from models import Correction, Error, ClozeList, ClozeSentence, Teacher, Student
import re


def create_cloze_list(list_name, target_word_list):
    print('Target words: ' + str(target_word_list))
    all_sentences = [correction.correct_sentence for correction in Correction.query.all()]
    target_words = [word.strip().replace("’", "'") for word in target_word_list]
    
    #Prepare regex patterns:
    regex_patterns = get_regex_patterns(target_words)
    
    #Find sentences with target words:
    sentences_with_target_words = []
    for sentence in all_sentences:
        for pattern  in regex_patterns:
            if pattern[0].search(sentence):
                if sentence not in sentences_with_target_words:
                    sentences_with_target_words.append(sentence)                
    print(str(sentences_with_target_words[:5]))

    #Create database list if there are any sentences:
    if sentences_with_target_words:
        
        if isinstance(current_user, Teacher):
            print('Teacher:', current_user.username)
            new_cloze_list = ClozeList(teacher_id=current_user.id, list_name=list_name,
                                       target_words='\n'.join(target_words))
        elif isinstance(current_user, Student):
            new_cloze_list = ClozeList(student_id=current_user.id, list_name=list_name,
                                       target_words='\n'.join(target_words))
            print('Student:', current_user.username)
        else:
            new_cloze_list = ClozeList(list_name=list_name,
                                       target_words='\n'.join(target_words))
            print('No current user')
            
        db.session.add(new_cloze_list)
        try:
            db.session.flush()
        except Exception as e:
            db.session.rollback()
            print(f"Error flushing new_cloze_list to the database: {e}")
            return
        print('Target words added to database: ' + str(new_cloze_list.target_words))
        
        #Build list of dictionaries with clozed sentences:
        unique_clozed_sentences = []
        sentence_dicts = []
        
        for sentence in sentences_with_target_words:  
            #Get clozed sentence and missing words:
            clozed_sentence, missing_words = get_clozed_sentence(sentence, regex_patterns)      
        
            if clozed_sentence not in unique_clozed_sentences:
                correction = Correction.query.filter_by(correct_sentence=sentence).first()
                error = Error.query.get(correction.error_id)
                unique_clozed_sentences.append(clozed_sentence)
                sentence_dict = {'clozed_sentence': clozed_sentence,
                                 'original_sentences': [sentence],
                                 'missing_words': missing_words,
                                 'error_id': error.id}
                sentence_dicts.append(sentence_dict)
            else:
                for dict in sentence_dicts:
                    if dict['clozed_sentence'] == clozed_sentence:
                        if sentence not in dict['original_sentences']:
                            dict['original_sentences'].append(sentence)
                        for i, word_list in enumerate(dict['missing_words']):
                            if missing_words[i][0] not in word_list:
                                word_list.append(missing_words[i][0])           
                                
        #Add new sentence to database:
        temp_dicts = []
        for dict in sentence_dicts:
            missing_words_joined = ['/'.join(word_list) for word_list in dict['missing_words']]
            new_cloze_sentence = ClozeSentence(original_sentences='\n'.join(dict['original_sentences']),
                                               clozed_sentence=dict['clozed_sentence'],
                                               missing_words='\n'.join(missing_words_joined),
                                               cloze_list_id=new_cloze_list.id,
                                               error_id = dict['error_id'])
            db.session.add(new_cloze_sentence)
            try:
                db.session.flush()
            except Exception as e:
                db.session.rollback()
                print(f"Error flushing new_cloze_sentence to the database: {e}")
                return
            #Create temporary list item for session:
            unique_target_words = []
            for word in target_words:
                if word.startswith('('):
                    word = word[word.find(')'):]
                elif word.endswith(')'):
                    word = word[:word.find('(')]
                if word.strip('.') not in unique_target_words:
                    unique_target_words.append(word.strip('.'))
            temp_dict = {'id': new_cloze_sentence.id,
                         'cloze_list_id': new_cloze_list.id,
                         'target_words': unique_target_words,
                         'original_sentences': dict['original_sentences'],
                         'clozed_sentence': dict['clozed_sentence'],
                         'missing_words': dict['missing_words'],
                         'error_id': dict['error_id'],
                         'correct_answers_needed': 3}
            temp_dicts.append(temp_dict)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error committing to the database: {e}")
            return []
        return temp_dicts
    return []

def get_regex_patterns(target_words):
    regex_patterns = []
    for word in target_words:
        if word.startswith('(') and ')' in word:
            base_word = word[word.find(')'):]
            prefix = word[1:word.find(')')]
            pattern = (re.compile(rf'\b{re.escape(prefix)}({re.escape(base_word)})\b', re.IGNORECASE), 1)
        elif word.endswith(')') and '(' in word:
            base_word = word[:word.find('(')]
            suffix = word[word.find('(')+1:word.find(')')]
            pattern = (re.compile(rf'\b({base_word}){suffix}\b', re.IGNORECASE), 1)
            print('Pattern: ' + str(pattern))
        else:
            base_word = word.strip('.')
            if word.startswith('...') and word.endswith('...'):
                pattern = (re.compile(rf'\B{re.escape(base_word)}\B', re.IGNORECASE), 0)
            elif word.startswith('...'):
                    pattern = (re.compile(rf'\B{re.escape(base_word)}(?!\w)', re.IGNORECASE), 0)
            elif word.endswith('...'):
                pattern = (re.compile(rf'(?<!\w){re.escape(base_word)}\B', re.IGNORECASE), 0)
            else:
                pattern = (re.compile(rf'(?<!\w){re.escape(base_word)}(?!\w)', re.IGNORECASE), 0)
        regex_patterns.append(pattern)
    print('regex_patterns = ' + str(regex_patterns))
    print('Compiled regex patterns: ' + str([pattern[0] for pattern in regex_patterns]))
    return regex_patterns

def get_clozed_sentence(sentence, regex_patterns):
    matches = []
    for pattern in regex_patterns:
        for match in pattern[0].finditer(sentence):
            matches.append((match.start(pattern[1]), match.end(pattern[1]), match.group(pattern[1]).lower()))
    print('Matches: ' + str(matches))
    matches.sort(reverse=True, key=lambda x: x[0])

    clozed_sentence = sentence
    missing_words = []

    for start, end, word in matches:
        print(f"Replacing '{clozed_sentence[start:end]}' with '____'")
        clozed_sentence = clozed_sentence[:start] + '____' + clozed_sentence[end:]
        missing_words.insert(0, [word])
    
    return clozed_sentence, missing_words

#def create_cloze_list(list_name, target_word_list):
#    print('Target words: ' + str(target_word_list))
#    all_sentences = [correction.correct_sentence for correction in Correction.query.all()]
#    #all_sentences = [correction.correct_sentence for correction in Correction.query.all()][:200]
#    target_words = [word.strip().replace("’", "'") for word in target_word_list]
#    
#    #Prepare regex patterns:
#    regex_patterns = []
#    for word in target_words:
#        if word.startswith('(') and ')' in word:
#            base_word = word[word.find(')'):]
#            prefix = word[1:word.find(')')]
#            pattern = (re.compile(rf'\b{re.escape(prefix)}({re.escape(base_word)})\b', re.IGNORECASE), 1)
#        elif word.endswith(')') and '(' in word:
#            base_word = word[:word.find('(')]
#            suffix = word[word.find('(')+1:word.find(')')]
#            pattern = (re.compile(rf'\b({base_word}){suffix}\b', re.IGNORECASE), 1)
#            print('Pattern: ' + str(pattern))
#        else:
#            base_word = word.strip('.')
#            if word.startswith('...') and word.endswith('...'):
#                pattern = (re.compile(rf'\B{re.escape(base_word)}\B', re.IGNORECASE), 0)
#            elif word.startswith('...'):
#                    pattern = (re.compile(rf'\B{re.escape(base_word)}(?!\w)', re.IGNORECASE), 0)
#            elif word.endswith('...'):
#                pattern = (re.compile(rf'(?<!\w){re.escape(base_word)}\B', re.IGNORECASE), 0)
#            else:
#                pattern = (re.compile(rf'(?<!\w){re.escape(base_word)}(?!\w)', re.IGNORECASE), 0)
#        regex_patterns.append(pattern)
#    print('Compiled regex patterns: ' + str([pattern[0] for pattern in regex_patterns]))
#    
#    #Find sentences with target words:
#    sentences_with_target_words = []
#    for sentence in all_sentences:
#        for pattern  in regex_patterns:
#            if pattern[0].search(sentence):
#                if sentence not in sentences_with_target_words:
#                    sentences_with_target_words.append(sentence)                
#    print(str(sentences_with_target_words[:5]))#

#    #Create database list if there are any sentences:
#    if sentences_with_target_words:
#        
#        if isinstance(current_user, Teacher):
#            print('Teacher:', current_user.username)
#            new_cloze_list = ClozeList(teacher_id=current_user.id, list_name=list_name,
#                                       target_words='\n'.join(target_words))
#        elif isinstance(current_user, Student):
#            new_cloze_list = ClozeList(student_id=current_user.id, list_name=list_name,
#                                       target_words='\n'.join(target_words))
#            print('Student:', current_user.username)
#        else:
#            new_cloze_list = ClozeList(list_name=list_name,
#                                       target_words='\n'.join(target_words))
#            print('No current user')
#            
#        db.session.add(new_cloze_list)
#        try:
#            db.session.flush()
#        except Exception as e:
#            db.session.rollback()
#            print(f"Error flushing new_cloze_list to the database: {e}")
#            return
#        print('Target words added to database: ' + str(new_cloze_list.target_words))
#        
#        #Build list of dictionaries with clozed sentences:
#        unique_clozed_sentences = []
#        sentence_dicts = []
#        
#        for sentence in sentences_with_target_words:        
#            matches = []
#            for pattern in regex_patterns:
#                for match in pattern[0].finditer(sentence):
#                    matches.append((match.start(pattern[1]), match.end(pattern[1]), match.group(pattern[1]).lower()))
#            print('Matches: ' + str(matches))
#            matches.sort(reverse=True, key=lambda x: x[0])
#            
#            clozed_sentence = sentence
#            missing_words = []
#            
#            for start, end, word in matches:
#                print(f"Replacing '{clozed_sentence[start:end]}' with '____'")
#                clozed_sentence = clozed_sentence[:start] + '____' + clozed_sentence[end:]
#                missing_words.insert(0, [word])
#            
#            if clozed_sentence not in unique_clozed_sentences:
#                correction = Correction.query.filter_by(correct_sentence=sentence).first()
#                error = Error.query.get(correction.error_id)
#                unique_clozed_sentences.append(clozed_sentence)
#                sentence_dict = {'clozed_sentence': clozed_sentence,
#                                 'original_sentences': [sentence],
#                                 'missing_words': missing_words,
#                                 'error_id': error.id}
#                sentence_dicts.append(sentence_dict)
#            else:
#                for dict in sentence_dicts:
#                    if dict['clozed_sentence'] == clozed_sentence:
#                        if sentence not in dict['original_sentences']:
#                            dict['original_sentences'].append(sentence)
#                        for i, word_list in enumerate(dict['missing_words']):
#                            if missing_words[i][0] not in word_list:
#                                word_list.append(missing_words[i][0])           
#                                
#        #Add new sentence to database:
#        temp_dicts = []
#        for dict in sentence_dicts:
#            missing_words_joined = ['/'.join(word_list) for word_list in dict['missing_words']]
#            new_cloze_sentence = ClozeSentence(original_sentences='\n'.join(dict['original_sentences']),
#                                               clozed_sentence=dict['clozed_sentence'],
#                                               missing_words='\n'.join(missing_words_joined),
#                                               cloze_list_id=new_cloze_list.id,
#                                               error_id = dict['error_id'])
#            db.session.add(new_cloze_sentence)
#            try:
#                db.session.flush()
#            except Exception as e:
#                db.session.rollback()
#                print(f"Error flushing new_cloze_sentence to the database: {e}")
#                return
#            #Create temporary list item for session:
#            unique_target_words = []
#            for word in target_words:
#                if word.startswith('('):
#                    word = word[word.find(')'):]
#                elif word.endswith(')'):
#                    word = word[:word.find('(')]
#                if word.strip('.') not in unique_target_words:
#                    unique_target_words.append(word.strip('.'))
#            temp_dict = {'id': new_cloze_sentence.id,
#                         'cloze_list_id': new_cloze_list.id,
#                         'target_words': unique_target_words,
#                         'original_sentences': dict['original_sentences'],
#                         'clozed_sentence': dict['clozed_sentence'],
#                         'missing_words': dict['missing_words'],
#                         'error_id': dict['error_id'],
#                         'correct_answers_needed': 3}
#            temp_dicts.append(temp_dict)
#        try:
#            db.session.commit()
#        except Exception as e:
#            db.session.rollback()
#            print(f"Error committing to the database: {e}")
#            return []
#        return temp_dicts
#    return []


  
  
def get_missing_words(clozed_sentence, original_sentences):
    gap_indices = [i for i in range(len(clozed_sentence)) if clozed_sentence.startswith('____', i)]
    sentence_chunks = []
    end_of_gap = gap_indices[0] + 4
    counter = 0
    for i in range(len(clozed_sentence)):
        if clozed_sentence.startswith('____', i):
            counter += 1
            if counter == len(gap_indices):
                sentence_chunk = clozed_sentence[end_of_gap:]
                sentence_chunks.append(sentence_chunk)
            else:
                sentence_chunk = clozed_sentence[end_of_gap:gap_indices[counter]]
                end_of_gap = gap_indices[counter] + 4
                sentence_chunks.append(sentence_chunk)
    starting_indices_list = []
    ending_indices_list = []
    missing_words = []
    for sentence in original_sentences:
        starting_indices = [gap_indices[0]]
        ending_indices = []
        counter2 = 0
        for i in range(len(sentence)):
            if sentence.startswith(sentence_chunks[counter2], i):
                if counter2 < len(sentence_chunks) - 1:
                    ending_indices.append(i)
                    starting_indices.append(i + len(sentence_chunks[counter2]))
                    counter2 += 1
                else:
                    ending_indices.append(i)
        for i in range(len(starting_indices)):
            if len(missing_words) > i:
                missing_word = sentence[starting_indices[i]:ending_indices[i]].lower()
                if missing_word not in missing_words[i]:
                    missing_words[i].append(missing_word)
            else:
                missing_word = sentence[starting_indices[i]:ending_indices[i]].lower()
                missing_word_choices = []
                missing_word_choices.append(missing_word)
                missing_words.append(missing_word_choices)
        
        starting_indices_list.append(starting_indices)
        ending_indices_list.append(ending_indices)
    
    return missing_words               

#def get_missing_words(clozed_sentence, original_sentences):
#    gap_indices = [i for i in range(len(clozed_sentence)) if clozed_sentence.startswith('____', i)]
#    starting_index = gap_indices[0] + 4
#    sentence_chunks = []
#    for gap_index in gap_indices:
#        sentence_chunk = clozed_sentence[starting_index:gap_index]
#        sentence_chunks.append(sentence_chunk)
#        starting_index += 4
#    sentence_chunks.append(clozed_sentence[starting_index:])
#    missing_words = []
#    for i in range(len(gap_indices)):
#        missing_words.append([])
#    for sentence in original_sentences:
        
    
    
    


#def create_cloze_list(list_name, target_word_list):
#    print('Target words: ' + str(target_word_list))
#    all_sentences = [correction.correct_sentence for correction in Correction.query.all()]
#    sentence_dicts = []
#    target_words = [word.lower().strip() for word in target_word_list]
#    sentences_with_target_words = []
#    for sentence in all_sentences:
#        sentence_words = [word.lower().strip(",.?!'’") for word in sentence.split()]
#        for word in target_words:
#            normalized_word = word.replace("’", "'")
#            if normalized_word in sentence_words and sentence not in sentences_with_target_words:
#                sentences_with_target_words.append(sentence)
#    if sentences_with_target_words:
#        new_cloze_list = ClozeList(list_name=list_name,
#                                   target_words='\n'.join(target_words))
#        db.session.add(new_cloze_list)
#        try:
#            db.session.flush()
#        except Exception as e:
#            db.session.rollback()
#            print(f"Error flushing new_cloze_list to the database: {e}")
#            return
#        print('Target words added to database: ' + str(new_cloze_list.target_words))
#        for sentence in sentences_with_target_words:
#            clozed_sentence_words = []
#            missing_words = []
#            for word in sentence.split():
#                normalized_word = word.replace("’", "'").lower().strip(",.?!'’")
#                if normalized_word in target_words:
#                    missing_words.append(normalized_word)
#                    gap = '_____'
#                    if word[-1] in ",.?!'’":
#                        gap += word[-1]
#                    clozed_sentence_words.append(gap)
#                else:
#                    clozed_sentence_words.append(word)
#            clozed_sentence = ' '.join(clozed_sentence_words)
#            correction = Correction.query.filter_by(correct_sentence=sentence).first()
#            error = Error.query.get(correction.error_id)
#            #Add new sentence to database:
#            new_cloze_sentence = ClozeSentence(original_sentence=sentence,
#                                               clozed_sentence=clozed_sentence,
#                                               missing_words='\n'.join(missing_words),
#                                               cloze_list_id=new_cloze_list.id,
#                                               error_id = error.id)
#            db.session.add(new_cloze_sentence)
#            #Create temporary list item for session:
#            sentence_dict = {'cloze_list_id': new_cloze_list.id,
#                             'target_words': target_words,
#                             'original_sentence': sentence,
#                             'clozed_sentence': clozed_sentence,
#                             'missing_words': missing_words,
#                             'error_id': error.id,
#                             'correct_answers_needed': 3}
#            sentence_dicts.append(sentence_dict)
#        try:
#            db.session.commit()
#        except Exception as e:
#            db.session.rollback()
#            print(f"Error committing to the database: {e}")
#            return []
#        return sentence_dicts
#    return []


