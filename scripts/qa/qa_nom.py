import pandas as pd
import ast
from qa import questions
from utils import few_shots


NOMINALIZATION_CONFIG = {
    "He": {
        "class_label": "פעולה",
        "few_shot_pred": few_shots.HEB_FEW_SHOT_FOR_NOMINALIZATION_PREDICTION,
        "few_shot_trans": few_shots.HEB_FEW_SHOT_FOR_NOM_CONSTRAIN_TRANSLATION,
    },
    "Ru": {
        "class_label": "действия",
        "few_shot_pred": few_shots.RU_FEW_SHOT_FOR_NOMINALIZATION_PREDICTION,
        "few_shot_trans": few_shots.RU_FEW_SHOT_FOR_NOM_CONSTRAIN_TRANSLATION,
    },
    "Fr": {
        "class_label": "action",
        "few_shot_pred": few_shots.FR_FEW_SHOT_FOR_NOMINALIZATION_PREDICTION,
        "few_shot_trans": few_shots.FR_FEW_SHOT_FOR_NOM_CONSTRAIN_TRANSLATION,
    }
}


def get_non_verb_predicates(df):
    return df.loc[df["reason"].astype(str).str.contains('there is no verb')].copy()


def filter_non_noun_predicates(df):
    # convert token_infos from str to list of dicts if needed
    if isinstance(df.iloc[0]['token_infos'], str):
        df['token_infos'] = df['token_infos'].apply(ast.literal_eval)
    filtered = []
    for _, row in df.iterrows():
        align_target = row['aligned_target_predicate']
        pred_idx = row['aligned_target_predicate_idx']
        chosen = row['chosen_predicate']
        word_ids = questions.get_word_id(pred_idx, align_target, chosen)
        if word_ids is None:
            continue
        is_noun = any(
            questions.get_token_by_id(wid, row['token_infos'])['U-POS'] == 'NOUN'
            for wid in word_ids
        )
        if is_noun:
            filtered.append(row)
    return pd.DataFrame(filtered)


def classify_predicates(df, few_shot, model, tokenizer):
    outputs = []
    for _, row in df.iterrows():
        prompt = f"{few_shot}{row['chosen_predicate']} :"
        encoded = tokenizer(prompt.strip(), return_tensors='pt').to(model.device)
        output = tokenizer.batch_decode(
            model.generate(**encoded, do_sample=False, max_new_tokens=17,
                           pad_token_id=tokenizer.eos_token_id)
        )[0]
        output_lines = output.strip().split('\n')
        label = output_lines[13] if len(output_lines) > 13 else ""
        row['classify_noun_predicate'] = label
        outputs.append(row)
    return pd.DataFrame(outputs)


def filter_by_class_label(df, label):
    return df.loc[df["classify_noun_predicate"].astype(str).str.contains(label)].copy()


def translate_nominal_questions(df, few_shot, model, tokenizer):
    for _, row in df.iterrows():
        nom_pred = row['chosen_predicate']
        en_q = row['question']
        translated = questions.get_output_from_llm(
            model, tokenizer, few_shot, c_prompt1=en_q, c_prompt2=nom_pred
        )
        df.at[row.name, 'translate_question'] = translated
    return df

def create_nominalization_questions(df, model, tokenizer, lang):
    config = NOMINALIZATION_CONFIG.get(lang)
    if config is None:
        raise ValueError(f"Unsupported language: {lang}")

    df = get_non_verb_predicates(df)
    df = filter_non_noun_predicates(df)
    df = classify_predicates(df, config["few_shot_pred"], model, tokenizer)
    df = filter_by_class_label(df, config["class_label"])
    df = translate_nominal_questions(df, config["few_shot_trans"], model, tokenizer)

    return df
