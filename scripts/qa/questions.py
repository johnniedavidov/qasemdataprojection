import ast
from utils import few_shots

FEW_SHOT_CONFIGS = {
    'He': {
        'question_generation': few_shots.HEB_FEW_SHOT_FOR_VERB_QUESTIONS,
        'predicate_decision': few_shots.HE_FEW_SHOT_FOR_PREDICATE_DECISION,
    },
    'Ru': {
        'question_generation': few_shots.RU_FEW_SHOT_FOR_VERB_QUESTIONS,
        'predicate_decision': few_shots.RU_FEW_SHOT_FOR_PREDICATE_DECISION,
    },
    'Fr': {
        'question_generation': few_shots.FR_FEW_SHOT_FOR_VERB_QUESTIONS,
        'predicate_decision': few_shots.FR_FEW_SHOT_FOR_PREDICATE_DECISION,
    },
    # Add more languages as needed here and ensure they have the necessary few-shot examples in few_shots.py.
}

def get_output_from_llm(model, tokenizer, few_shot, c_prompt1, c_prompt2):
    c_prompt = f'{c_prompt1} | {c_prompt2}'
    prompt = few_shot + c_prompt
    
    encoded = tokenizer(prompt.strip(), return_tensors='pt').to(model.device)
    output = model.generate(**encoded, do_sample=False, max_new_tokens=17, pad_token_id=tokenizer.eos_token_id, return_dict_in_generate=False)
    output = tokenizer.batch_decode(output)[0][len(prompt) - 2:]
    output = output.split('\n')
    return output[1]

def find_index(row, predicate):
    target_words = row['aligned_target_predicate']
    target_indices = row['aligned_target_predicate_idx']
    if predicate in target_words:
        idx = target_words.index(predicate)
        return str(target_indices[idx])
    return None

def choose_one_predicate(df, few_shot, model, tokenizer):
    df["chosen_predicate"] = ''
    for index, row in df.iterrows():
        predicate_text = row['predicate_text']
        cand_predicate = row['aligned_target_predicate']
        list_of_target_idx = row['aligned_target_predicate_idx'] 
        if len(cand_predicate) <= 1:
            df.at[index, 'chosen_predicate'] = cand_predicate[0]
            df.at[index, 'target_predicate_idx'] = list_of_target_idx[0]
            continue
        predicate = get_output_from_llm(model, tokenizer, few_shot,
                                            c_prompt1=predicate_text,
                                            c_prompt2=cand_predicate)
        df.at[index, 'chosen_predicate'] = str(predicate)
        df.at[index, 'target_predicate_idx'] = find_index(row, predicate)

    return df

def get_token_by_id(word_id, token_infos):
    for token_info in token_infos:
        if token_info['WORD_ID'] == word_id + 1:
            return token_info
    return None

def get_word_id(target_indices, aligned_words, predicate):
    def contains_word(s, w):
        return f' {w} ' in f' {s} '

    if len(target_indices) == 1:
        return [target_indices[0]]

    matched = [idx for idx, word in zip(target_indices, aligned_words) if contains_word(predicate, word)]
    return matched if matched else None

def check_verb_predicate(row):
    """
    verify that word id is indeed verb.
    """
    aligned_words = row['aligned_target_predicate']
    target_indices = row['aligned_target_predicate_idx']
    chosen = row['chosen_predicate']      
    word_ids = get_word_id(target_indices, aligned_words, chosen)
    
    if word_ids is None:
        return 'incorrect token_infos indexer'
    token_infos = row['token_infos']
    is_verb = False
    for word_id in word_ids:
        token_info = get_token_by_id(word_id, token_infos)
        if token_info is None:
            return 'incorrect token_infos indexer'
        if token_info['U-POS'] == 'VERB':
            is_verb = True
    if is_verb == False:
        return f'there is no verb in {aligned_words}'
    return None

def safe_literal_eval(x):
    if isinstance(x, str):
        return ast.literal_eval(x)
    return x

def create_questions(qa_df, model, tokenizer, lang):
    """
    generate hebrew translate questions and save the high similarity
    to the source english questions from df_qa_heb.
    """
    qa_df['aligned_target_predicate'] = qa_df['aligned_target_predicate'].apply(safe_literal_eval)
    qa_df['aligned_target_predicate_idx'] = qa_df['aligned_target_predicate_idx'].apply(safe_literal_eval)
    qa_df['token_infos'] = qa_df['token_infos'].apply(safe_literal_eval)
    
    few_shot_questions = FEW_SHOT_CONFIGS[lang]['question_generation']
    few_shot_pred_decision = FEW_SHOT_CONFIGS[lang]['predicate_decision']
    qa_df = choose_one_predicate(qa_df, few_shot_pred_decision, model, tokenizer)
    qa_df['translate_question'] = ''
    qa_df['reason'] = ''
    for index, row in qa_df.iterrows():
        if index % 100 == 0:
            print(f"Processed {index} rows")
        en_question = row['question']
        reason = check_verb_predicate(row)
        if reason is not None:
            qa_df.at[index, 'reason'] = reason
            continue
        
        predicate = row['chosen_predicate']
        # get dicta translate question
        translate_question = get_output_from_llm(model, tokenizer, few_shot= few_shot_questions,  
                                                 c_prompt1=en_question,
                                                 c_prompt2=predicate)

        qa_df.at[index, 'translate_question'] = translate_question
    return qa_df
