from typing import Dict, Tuple, Union, Optional
import csv
import pandas as pd
from utils import utils_func


def translate_he2en(text, model, tokenizer):
    return utils_func.translate(text=text, tokenizer=tokenizer, model=model)


def translate_loop(sentences, model, tokenizer, MAX_IN=100):
    out = []
    for i in range(len(sentences) // MAX_IN + 1):
        print(f"Translating {i * MAX_IN} to {(i + 1) * MAX_IN}")
        out.extend(translate_he2en(text=sentences[i * MAX_IN: (i + 1) * MAX_IN], model=model, tokenizer=tokenizer))
    return out


def get_sentences_from_conll(ud_fn, sep=','):
    def read_word_id_range(raw_id: str) -> Union[Tuple[int, int], int]:
        if "-" in raw_id:
            src, dst = raw_id.split("-")
            return int(src), int(dst)
        elif "." in raw_id:
            return float(raw_id)
        else:
            return int(raw_id)

    def read_features(raw_feats: str) -> Optional[Dict[str, str]]:
        raw_feats = raw_feats.strip('"')
        if not raw_feats or raw_feats == "_":
            return None
        else:
            kv_pairs = raw_feats.split("|")
            return dict([kv.split("=") for kv in kv_pairs if kv])

    with open(ud_fn, encoding="utf8") as fin:
        english_text, sent_id, sent, token_infos = None, None, None, []
        COLUMNS = "WORD_ID,FORM,LEMMA,U-POS,X-POS,FEATS".split(',')
        reader = csv.reader(fin, delimiter=sep, quotechar=None if sep == "\t" else '"')
        for line in reader:
            if len(line) == 0 or line[0] == '':  # empty line end of block
                tokens = [t['FORM'] for t in token_infos if isinstance(t['WORD_ID'], int)]
                yield {"sent_id": sent_id,
                    "sentence": sent,
                    "english_text": english_text,
                    "tokens": tokens,
                    "token_infos": token_infos}
                sent, sent_id = None, None
            elif line[0].startswith("# sent_id = "):
                sent_id = line[0][len("# sent_id = "):]
            elif line[0].startswith('# text ='):
                sent = line[0][len('# text ='):].strip()
                token_infos = []
            elif line[0].startswith("# english_text = "):
                english_text = line[0][len("# english_text = "):]
            elif line[0].startswith("# text_en = "):
                english_text = line[0][len("# text_en = "):]
            elif line[0].startswith("# sound_url = "):
                pass
            elif line[0].startswith("# speaker = "):
                pass
            elif line[0].startswith("# source = "):
                pass
            elif line[0].startswith("# source_url = "):
                pass
            elif line[0].startswith("# note"):
                pass

            elif sent and sent_id:  # a token row
                token_info_raw_list = line[:len(COLUMNS)]
                token_info = dict(zip(COLUMNS, token_info_raw_list))
                token_info["WORD_ID"] = read_word_id_range(token_info["WORD_ID"])
                token_info["FEATS"] = read_features(token_info["FEATS"])
                token_infos.append(token_info)


def get_info_from_morphological_tagging(ud_path, model, tokenizer, nlp_model, sep='\t'):
    sentences = list(get_sentences_from_conll(ud_fn=ud_path, sep=sep))
    sent_list = [s["sentence"] for s in sentences]
    translated = [s['english_text'] for s in sentences]

    print(f"Translating {len(sent_list)} sentences")
    if translated[0] is None:
        translated = translate_loop(sent_list, model=model, tokenizer=tokenizer)

    rec = [dict(sent_id=s["sent_id"],
                sentence=s["sentence"],
                tokenized_sentence=' '.join(s["tokens"]),
                base_sentence=trans,
                en_tokens=" ".join([tkn.text for tkn in nlp_model(trans)]),
                token_infos=s["token_infos"])
           for s, trans in zip(sentences, translated)]

    return pd.DataFrame(rec)
