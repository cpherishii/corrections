if request.method == 'POST' and edit_form.validate_on_submit():
    incorrect_sentence = request.form['error']
    correct_sentences = request.form['correction'].split('\n')
    topics = None
    rules = None
    rule_topic_ids = None
    if request.form['topic1']:
        topics = []
        topics.append(Topic.query.get(request.form['topic1']).topic_name)
    if request.form['topic2']:
        topics.append(Topic.query.get(request.form['topic2']).topic_name)
    if request.form['topic3']:
        topics.append(Topic.query.get(request.form['topic3']).topic_name)
    if request.form['rule1']:
        rules = []
        rules.append(Rule.query.get(request.form['rule1']).rule_name)
    if request.form['rule2']:
        rules.append(Rule.query.get(request.form['rule2']).rule_name)
    if request.form['rule3']:
        rules.append(Rule.query.get(request.form['rule3']).rule_name)
    edit_error(error_id, incorrect_sentence, correct_sentences, topics, rules, rule_topic_ids)