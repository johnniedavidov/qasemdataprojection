import pandas as pd
import ast
from typing import Dict, List
import re
import itertools
from utils import utils_func

Alignment = Dict[int, List[int]]
ListOfSuffixesHEB = ['ה', '_ה_', '_ב_', 'ל', 'ו', 'כ', '_של_', 'של', 'ב', 'ש']

ListOfSuffixes_RU = ['и', 'в', 'с', 'у', 'на', 'по', 'о', 'об', 'за', 'из', 'от', 'до', 'без', 'для', 'при']

ListOfSuffixes_FR = ['à', 'de', 'en', 'et', 'du', 'au', 'aux', 'des', 'le', 'la', 'les']


def remove_suffixes_from_end_heb(answer_tokens):
    while answer_tokens and answer_tokens[-1] in ListOfSuffixesHEB:
        answer_tokens = answer_tokens[:-1]
    return answer_tokens

def remove_suffixes_from_end_rus(answer_tokens):
    while answer_tokens and answer_tokens[-1].lower() in ListOfSuffixes_RU:
        answer_tokens = answer_tokens[:-1]
    return answer_tokens

def remove_suffixes_from_end_fr(answer_tokens):
    while answer_tokens and answer_tokens[-1].lower() in ListOfSuffixes_FR:
        answer_tokens = answer_tokens[:-1]
    return answer_tokens

def remove_suffixes_by_lang(answer_tokens, lang):
    if lang == 'He':
        return remove_suffixes_from_end_heb(answer_tokens)
    elif lang == 'Ru':
        return remove_suffixes_from_end_rus(answer_tokens)
    elif lang == 'Fr':
        return remove_suffixes_from_end_fr(answer_tokens)
    # For other languages, you can add more conditions here.
    else:
        return answer_tokens  # fallback

def get_heb_answer_and_idxs(aligned_idxs, tokens, lang: str) -> (str, List[int]):
    answer_tokens = [tokens[i] for i in aligned_idxs]
    answer_tokens = remove_suffixes_by_lang(answer_tokens=answer_tokens, lang=lang)
    dst_answer = " ".join(answer_tokens)
    return dst_answer, aligned_idxs


def get_best_aligned_answers(src_answer: str, alignment: Alignment, src_tokens: List[str], dst_tokens: List[str],
                             predicate: str, lang: str) -> str:
    """
    Given a QASem answer span in src language, and an alignment from FastAlign (+ the parallel sentences),
    extract the corresponding answer span in dst language, by applying the alignment per token.
    """
    def fill_miss_idxs(lst):
        if lst:
            n1 = lst[0]
            n2 = lst[-1]
            lst[:] = range(n1, n2 + 1)
        return lst

    def improve_answers(ans_str, ans_idx, sent_tokens):
        """
        """
        def find_new_idx(str_ans, old_ans_idx, list_dst_tokens):
            list_str_ans = str_ans.split()
            new_idx = old_ans_idx.copy()
            for idx in old_ans_idx:
                if list_dst_tokens[idx] not in list_str_ans:
                    new_idx.remove(idx)
            return new_idx

        # spilt the answer if there is "." in the string.
        res = re.split('\.', ans_str)

        if len(res) <= 1:
            if not pd.isnull(predicate):
                res = re.split(re.escape(predicate), res[0])
            if len(res) <= 1:
                return ans_str, ans_idx

        new_ans = max(res, key=len).strip()
        if not pd.isnull(predicate):
            # res = re.split(predicate, new_ans)
            res = re.split(re.escape(predicate), new_ans)
            new_ans = max(res, key=len).strip()
        new_dst_idx = find_new_idx(new_ans, ans_idx, sent_tokens)

        return new_ans, new_dst_idx

    tok_answer = [t.lower() for t in src_answer.split()]
    src_tokens = [t.lower() for t in src_tokens]
    src_answer_first_idx = utils_func.find_first_idx_sublist(lst=src_tokens, sublist=tok_answer)
    assert src_answer_first_idx is not None, f"answer '{src_answer}' is not found in tokenized sentence {src_tokens}"
    src_answer_next_last_idx = src_answer_first_idx + len(tok_answer)
    src_answer_idxs = set(range(src_answer_first_idx, src_answer_next_last_idx))  # all induced in range
    # apply alignment
    dst_aligned_idxs = fill_miss_idxs(list(sorted(set(itertools.chain(*[alignment.get(src_idx, []) for
                                                                        src_idx in src_answer_idxs])))))
    answer, dst_idxs = get_heb_answer_and_idxs(dst_aligned_idxs, dst_tokens, lang)
    answer, new_idxs = improve_answers(ans_str=answer, ans_idx=dst_idxs, sent_tokens=dst_tokens)
    return answer

def create_verb_qasem_from_answers(answers_df):
    """
    Create the final QASem dataframe using only the answers_df,
    keeping all the desired columns for full downstream usage.
    """

    # List of all required columns
    required_columns = [
        'sent_id',
        'base_sentence',
        'base_tokens',
        'target_sentence',
        'tok_target_sentence',
        'question',
        'answers',
        'predicate_idx',
        'predicate_text',
        'verb_form',
        'type',
        'question_role',
        'token_infos',
        'aligned_target_answers',
        'aligned_target_predicate_idx',
        'aligned_target_predicate',
        'base_target_idx_alignment',
        'base_target_str_alignment',
        'chosen_predicate',
        'translate_question',
        'new_aligned_target_answers'
    ]

    # Check for missing columns
    missing_cols = [col for col in required_columns if col not in answers_df.columns]
    if missing_cols:
        raise ValueError(f"The following required columns are missing from answers_df: {missing_cols}")

    # Filter valid rows (optional)
    filtered_df = answers_df[
        answers_df['translate_question'].notnull() &
        answers_df['translate_question'].str.strip().ne('') &
        answers_df['new_aligned_target_answers'].notnull()
    ]

    # Reorder and return
    final_df = filtered_df[required_columns].reset_index(drop=True)

    return final_df

def get_answers(df, ud_align_df, lang: str) -> pd.DataFrame:
    # take a sample for inspection
    df['new_aligned_target_answers'] = ''
    for index, row in df.iterrows():
        answers = ast.literal_eval(row['answers'])
        predicate = row['chosen_predicate']
        # Get Sentence--Sentence alignment
        alignment_row = utils_func.get_row_by_sent_id(ud_align_df, str(row['sent_id']))
        if isinstance(row['base_target_idx_alignment'], str):
            idx_alignment = ast.literal_eval(row['base_target_idx_alignment'])
        else:
            idx_alignment = row['base_target_idx_alignment']

        tok_target_sent = alignment_row["target_tokens"].split(" ")
        tok_base_sent = alignment_row[f"base_tokens"].split(" ")
        # check for (Eng) predicate alignment to Heb

        # Translate QA
        new_aligned_target_answers = [get_best_aligned_answers(src_answer=eng_answer, alignment=idx_alignment,
                                                            src_tokens=tok_base_sent, dst_tokens=tok_target_sent,
                                                            predicate=predicate, lang=lang)
                                   for eng_answer in answers]
        if index % 100 == 0:
            print(f"Processed {index} rows")
        df.at[index, 'new_aligned_target_answers'] = new_aligned_target_answers
        df.at[index, 'base_tokens'] = alignment_row['base_tokens']

    df = create_verb_qasem_from_answers(df)
    return df
