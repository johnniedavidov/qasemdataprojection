from typing import Iterable, Union, Optional
import torch


def find_first_idx_sublist(lst, sublist) -> Optional[int]:
        # as str.index for list - return the index of the sublist if occurring in list, None otherwise
        size = len(sublist)
        for i in range(len(lst)):
            if lst[i:i + size] == sublist:
                return i
        return None

def get_row_by_sent_id(ud_df, sent_id: str):
    for _, r in ud_df.iterrows():
        if r['sent_id'] == sent_id:
            return r
    return None


def translate(text: Union[str, Iterable[str]], tokenizer, model):
    list_text = [text] if isinstance(text, str) else text
    out = []
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    for t in list_text:
        # print(f"Translating: {t}")
        input_ids = tokenizer(t, return_tensors="pt", padding=True, truncation=True).to(device)
        outputs = model.generate(**input_ids)
        translate_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        out.append(translate_text)
    if isinstance(text, str):
        return out[0]
    else:
        return out

