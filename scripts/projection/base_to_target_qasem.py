import pandas as pd
from typing import Dict, Optional, List
from collections import defaultdict
import itertools
from utils import utils_func
import ast

Alignment = Dict[int, List[int]]

def get_aligned_answer(src_answer: str, alignment: Alignment, src_tokens: List[str], dst_tokens: List[str]) -> str:
    """
    Given a QASem answer span in src language, and an alignment from FastAlign (+ the parallel sentences),
    extract the corresping answer span in dst language, by applying the alignment per token.
    """

    def listFindSublist(lst, sublist) -> Optional[int]:
        # as str.index for list - return the index of the sublist if occurring in list, None otherwise
        size = len(sublist)
        for i in range(len(lst)):
            if lst[i:i + size] == sublist:
                return i
        return None

    tok_answer = [t.lower() for t in src_answer.split()]
    src_tokens2 = [t.lower() for t in src_tokens]
    src_answer_idx_start = listFindSublist(lst=src_tokens2, sublist=tok_answer)
    assert src_answer_idx_start is not None, f"answer '{src_answer}', tok_answer {tok_answer} is not found in tokenized sentence {src_tokens}, src_tokens2 {src_tokens2}"
    src_answer_idx_end = src_answer_idx_start + len(tok_answer)
    src_answer_idxs = set(range(src_answer_idx_start, src_answer_idx_end))  # all indiced in range
    # apply alignment
    dst_aligned_idxs = list(sorted(set(itertools.chain(*[alignment.get(src_idx, []) for src_idx in src_answer_idxs]))))
    dst_answer_toks = [dst_tokens[i] for i in dst_aligned_idxs]
    return " ".join(dst_answer_toks)


def csv_row_to_alignment(src_token, dst_token, candidate_alignment):
    """
    dir of alignments - e.g. 'he-en' or 'en-he'.
    """

    def read_single_alignment(raw_align_str) -> Alignment:
        d = defaultdict(list)
        for pair in raw_align_str.split():
            src_id, dst_id = pair.split('-')
            d[int(src_id)].append(int(dst_id))
        return dict(d)

    def apply_alignment_on_tokens(alignment: Alignment, src_tokens: List[str], dst_tokens: List[str]) \
            -> Dict[str, List[str]]:
        """
        Translate alignment from indices to token strings
        (fails on collisions i.e. repeated tokens)
        """
        d = {}
        for src_id, dst_ids in alignment.items():
            d[src_tokens[src_id]] = [dst_tokens[dst_id] for dst_id in dst_ids]
        return d

    idx_alignment = read_single_alignment(candidate_alignment)
    str_alignment = apply_alignment_on_tokens(idx_alignment, src_token.split(), dst_token.split())
    return idx_alignment, str_alignment


def serialize_answers(val):
    if isinstance(val, list):
        return str(val)
    elif isinstance(val, str):
        return val
    elif pd.isna(val):
        return "[]"
    else:
        raise TypeError(f"Unexpected type in answers column: {type(val)}")

def align_qasem_base_to_target(base_qasem_df, aligned_ud_df):
    def get_qa_from_row(row):
        """ (predicate, predicate_idx, question, answers) """
        return row.predicate_text, row.predicate_idx, row.question, ast.literal_eval(row.answers)

    aligned_predicates = []
    qasrl_qas = base_qasem_df[base_qasem_df.type == "VERB"]
    qanom_qas = base_qasem_df[base_qasem_df.type == "NOUN"]
    print(f"len qasrl: {len(qasrl_qas)}")
    print(f"len qanom: {len(qanom_qas)}")
    base_qasem_df['answers'] = base_qasem_df['answers'].apply(serialize_answers)

    recs2 = []
    for _, row in base_qasem_df.iterrows():
        # Get Sentence--Sentence alignment
        alignment_row = utils_func.get_row_by_sent_id(aligned_ud_df, str(row['sent_id']))
        base_token = alignment_row["base_tokens"]
        target_token = alignment_row["target_tokens"]
        base_tgt_alignment = alignment_row["base_target_alignments"]
        idx_alignment, str_alignment = csv_row_to_alignment(src_token=base_token, dst_token=target_token,
                                                            candidate_alignment=base_tgt_alignment)
        tok_tgt_sent = target_token.split(" ")
        tok_base_sent = base_token.split(" ")
        # check for (Eng) predicate alignment to Heb
        aligned_tgt_predicate_idx = idx_alignment.get(row.predicate_idx, None)
        if aligned_tgt_predicate_idx is None:
            aligned_predicates.append(dict(**row))
            continue
        aligned_tgt_predicate = [tok_tgt_sent[idx] for idx in aligned_tgt_predicate_idx]
        # Translate QA
        qa = get_qa_from_row(row)  # English QA
        
        aligned_tgt_answers = [get_aligned_answer(src_answer=eng_answer, alignment=idx_alignment,
                                                    src_tokens=tok_base_sent, dst_tokens=tok_tgt_sent)
                                for eng_answer in qa[3]]
        rec = dict(**row,
                    aligned_target_answers=aligned_tgt_answers,
                    aligned_target_predicate_idx=aligned_tgt_predicate_idx,
                    aligned_target_predicate=aligned_tgt_predicate,
                    base_target_idx_alignment=idx_alignment,
                    base_target_str_alignment=str_alignment,
                    )
        recs2.append(rec)

    return pd.DataFrame(recs2)