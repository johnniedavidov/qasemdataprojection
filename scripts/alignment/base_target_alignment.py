import time
import pandas as pd
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import cpu_count


def represent_alignment(alignments: dict, src: str, trg: str):
    formatted_list = [f"{item[0]}-{item[1]}" for item in alignments['mwmf']]
    return ' '.join(formatted_list)


def process_row(args):
    row_dict, aligner = args
    target_tokens = row_dict['tokenized_sentence']
    base_tokens = row_dict['en_tokens']

    base_target_alignments = aligner.get_word_aligns(base_tokens, target_tokens)
    base_target_str = represent_alignment(base_target_alignments, src='base', trg='target')

    return {
        'sent_id': row_dict['sent_id'],
        'base_tokens': base_tokens,
        'target_tokens': target_tokens,
        'token_infos': row_dict['token_infos'],
        'target_sentence': row_dict['sentence'],
        'base_sentence': row_dict['base_sentence'],
        'base_target_alignments': base_target_str,
    }


def get_alignment(df_ud, aligner, num_processes=None) -> pd.DataFrame:
    """
    Computes word alignment between base and target tokens using multi-threading.

    Args:
        df_ud (pd.DataFrame): DataFrame with columns 'en_tokens', 'tokenized_sentence', etc.
        aligner (SimAlign): Preloaded SimAlign aligner.
        num_processes (int, optional): Number of threads to use. Defaults to cpu_count().

    Returns:
        pd.DataFrame: A DataFrame with alignment results per sentence.
    """
    print("Starting alignment with multiprocessing...")

    rows = df_ud.to_dict(orient='records')
    if num_processes is None:
        num_processes = cpu_count()

    print(f"Using {num_processes} threads for alignment.")
    start = time.time()
    results = []

    with ThreadPool(processes=num_processes) as pool:
        for i, res in enumerate(pool.imap(process_row, [(row, aligner) for row in rows]), start=1):
            results.append(res)
            if i % 50 == 0 or i == len(rows):
                elapsed = round(time.time() - start, 2)
                print(f"{i}/{len(rows)} rows processed - {elapsed} sec elapsed")

    print(f"Finished alignment in {round(time.time() - start, 2)} seconds using {num_processes} threads.")
    return pd.DataFrame(results)