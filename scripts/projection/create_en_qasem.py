import pandas as pd
from qasem_parser import QasemParser, QasemFrame


def pars_the_frames(df, qa_parser: QasemParser, num_start_rows: int, num_end_rows: int) -> QasemFrame:

    translated = [tr for tr in df['base_tokens'][num_start_rows:num_end_rows]]
    orig_sentences = [o_s for o_s in df['target_sentence'][num_start_rows:num_end_rows]]
    orig_tok_sentences = [o_t_s for o_t_s in df['target_tokens'][num_start_rows:num_end_rows]]
    sent_ids = [sent_id for sent_id in df['sent_id'][num_start_rows:num_end_rows]]
    tok_infos = [t_i for t_i in df['token_infos'][num_start_rows:num_end_rows]]

    # split sentences by spaces using split()
    split_translated = [tr.split() for tr in translated if tr is not None]
    frames = qa_parser(split_translated)

    qasrl_qas = [dict(
                      sent_id=sent_id, base_sentence=eng_s, target_sentence=tgt_s, tok_target_sentence=tok_tgt_s,
                      question=qa.question, answers=[qa.text],
                      predicate_idx=pred_info.predicate.index,
                      predicate_text=pred_info.predicate.text, verb_form=pred_info.predicate.lemma,
                      type=pred_info.predicate.pos, question_role=qa.role, token_infos=tok_inf)
                 for sent_id, eng_s, tgt_s, tok_tgt_s, frame, tok_inf in
                 zip(sent_ids, translated, orig_sentences, orig_tok_sentences, frames, tok_infos)
                 for pred_info in frame for qa in pred_info.arguments]
    return pd.DataFrame(qasrl_qas)
