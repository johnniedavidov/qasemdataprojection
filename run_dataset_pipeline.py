import os
import sys
import argparse
from pathlib import Path

import pandas as pd
import torch
import spacy
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForCausalLM
from simalign import SentenceAligner

# for compatibility with the current directory structure
sys.path.append(str(Path(__file__).parent / "scripts"))

# importing modules from the scripts directory
from preprocess import conll_to_df
from alignment import base_target_alignment
from projection import create_en_qasem, base_to_target_qasem
from qa import questions, answers, qa_nom
from utils import utils_func, few_shots
from qasem_parser import QasemParser 


def parse_arguments():
    parser = argparse.ArgumentParser(description="Run full QASem projection pipeline")

    parser.add_argument("--lang", type=str, required=True,
                        help="Target language code: He, Ru, Fr")
    parser.add_argument("--ud_path", type=str, required=True,
                        help="Path to the UD .conllu file")
    parser.add_argument("--preprocessing", action="store_true",
                        help="If set, will preprocess UD and create alignments")
    parser.add_argument("--skip_parsing", action="store_true",
                        help="If set, skips English QASem parsing step")
    parser.add_argument("--source", type=str, required=True,
                        help="Dataset source name (e.g., wiki, htb, gsd)")
    parser.add_argument("--num_start_rows", type=int, default=0,
                        help="Start index of the rows to process")
    parser.add_argument("--num_end_rows", type=int,
                        help="End index (exclusive) of the rows to process, default: num_start_rows + 100")

    return parser.parse_args()

def get_models_by_lang(lang_code: str):
    """
    Load the appropriate models (translation + LLM) based on the target language.
    """
    if lang_code == "He":
        translation_model_name = "Helsinki-NLP/opus-mt-tc-big-he-en"
        llm_model_name = "dicta-il/dictalm2.0"
    elif lang_code == "Ru":
        translation_model_name = "Helsinki-NLP/opus-mt-ru-en"
        llm_model_name = "sambanovasystems/SambaLingo-Russian-Base"
    elif lang_code == "Fr":
        translation_model_name = "Helsinki-NLP/opus-mt-tc-big-fr-en"
        llm_model_name = "OpenLLM-France/Claire-7B-FR-Instruct-0.1"
    # For new languages, you can add more conditions here, need a translation model and a suitable LLM.
    else:
        raise ValueError(f"Unsupported language code: {lang_code}")

    # Load translation model
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    translation_model = AutoModelForSeq2SeqLM.from_pretrained(translation_model_name).to(device)
    translation_tokenizer = AutoTokenizer.from_pretrained(translation_model_name)

    # Load LLM
    llm_model = AutoModelForCausalLM.from_pretrained(
        llm_model_name,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        load_in_4bit=True
    )

    llm_model.config.return_dict = True

    llm_tokenizer = AutoTokenizer.from_pretrained(llm_model_name)

    return translation_model, translation_tokenizer, llm_model, llm_tokenizer


class QASemProjection:
    def __init__(self, args):
        self.args = args
        self.lang = args.lang
        self.source = args.source
        self.raw_output_dir = Path("preprocessed_data") / f"{self.lang}_{self.source}"
        self.final_dataset_dir = Path("generated_qasem_data") / f"{self.lang}_{self.source}"

        self.raw_output_dir.mkdir(parents=True, exist_ok=True)
        self.final_dataset_dir.mkdir(parents=True, exist_ok=True)

        # Load models
        self.translation_model, self.translation_tokenizer, \
        self.llm_model, self.llm_tokenizer = get_models_by_lang(self.lang)

        # Load other components
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.nlp = spacy.load("en_core_web_sm")
        self.aligner = SentenceAligner(model="bert", token_type="bpe", matching_methods="m")
        self.parser = QasemParser.from_pretrained("cattana/flan-t5-large-qasem-joint-tokenized", batch_size=4, device="cuda", torch_dtype=torch.float16)

        # Setup I/O paths
        self.num_start = args.num_start_rows
        self.num_end = args.num_end_rows
        self.ud_input_path = args.ud_path
        self.ud_df = None
        self.aligned_ud_df = None
        self.base_qasem_df = None
        self.target_qasem_df = None
        self.verb_questions_df = None
        self.verb_qasem_df = None
        self.nom_questions_df = None
        self.nom_qasem_df = None
        self.combined_qasem_df = None

        if self.num_end is None:
            self.num_end = self.num_start + 100

    def preprocess(self):
        print("Preprocessing UD data and creating alignments...")

        self.ud_df = conll_to_df.get_info_from_morphological_tagging(
            ud_path=self.ud_input_path,
            model=self.translation_model,
            tokenizer=self.translation_tokenizer,
            nlp_model=self.nlp,
            sep='\t'
        )

        ud_df_path = self.raw_output_dir / "UD-tokenized-translated.csv"
        self.ud_df.to_csv(ud_df_path, index=False)

        self.aligned_ud_df = base_target_alignment.get_alignment(df_ud=self.ud_df, aligner=self.aligner)
        aligned_path = self.raw_output_dir / "UD-tokenized-translated-aligned.csv"
        self.aligned_ud_df.to_csv(aligned_path, index=False)

    def run_parser(self):
        print("Running QASem parser on English projection...")
        if self.aligned_ud_df is None:
            aligned_path = self.raw_output_dir / "UD-tokenized-translated-aligned.csv"
            self.aligned_ud_df = pd.read_csv(aligned_path, dtype={'sent_id': str})

        self.base_qasem_df = create_en_qasem.pars_the_frames(
            df=self.aligned_ud_df,
            qa_parser=self.parser,
            num_start_rows=self.num_start,
            num_end_rows=self.num_end
        )

        base_path = self.raw_output_dir / f"base-qasem-{self.num_start}-{self.num_end}.csv"
        self.base_qasem_df.to_csv(base_path, index=False)

    def project_to_target(self):
        print("Projecting QASem to target language...")
        if self.base_qasem_df is None:
            base_path = self.raw_output_dir / f"base-qasem-{self.num_start}-{self.num_end}.csv"
            self.base_qasem_df = pd.read_csv(base_path, dtype={'sent_id': str})

        if self.aligned_ud_df is None:
            aligned_path = self.raw_output_dir / f"UD-tokenized-translated-aligned.csv"
            self.aligned_ud_df = pd.read_csv(aligned_path, dtype={'sent_id': str})

        self.target_qasem_df = base_to_target_qasem.align_qasem_base_to_target(
            base_qasem_df=self.base_qasem_df,
            aligned_ud_df=self.aligned_ud_df
        )

        target_path = self.raw_output_dir / f"aligned-target-qasem-{self.num_start}-{self.num_end}.csv"
        self.target_qasem_df.to_csv(target_path, index=False)


    def generate_questions(self):
        print("Generating target verb questions...")

        # Load target_qasem_df if not already loaded
        if self.target_qasem_df is None:
            self.target_qasem_df = pd.read_csv(self.target_qasem_path, dtype={'sent_id': str})

        # Create questions
        verb_questions_df = questions.create_questions(
            qa_df=self.target_qasem_df,
            model=self.llm_model,
            tokenizer=self.llm_tokenizer,
            lang=self.args.lang
        )

        # Save to file
        self.verb_questions_df_path = self.raw_output_dir / f"QASRL-questions-{self.num_start}-{self.num_end}.csv"
        verb_questions_df.to_csv(self.verb_questions_df_path, index=False)

        # Also keep in memory for next stages
        self.verb_questions_df = verb_questions_df

        print(f"Saved verb questions to {self.verb_questions_df_path}")
        
    def generate_answers(self):
        print("Generating answers for translated questions...")

        if self.aligned_ud_df is None:
            aligned_path = self.raw_output_dir / "UD-tokenized-translated-aligned.csv"
            self.aligned_ud_df = pd.read_csv(aligned_path, dtype={'sent_id': str})
        
        if self.verb_questions_df is None:
            verb_questions_df_path = {self.raw_output_dir} / f"QASRL-questions-{self.num_start}-{self.num_end}.csv"
            self.verb_questions_df = pd.read_csv(verb_questions_df_path, dtype={'sent_id': str})

        # Generate answers
        self.verb_qasem_df = answers.get_answers(df=self.verb_questions_df,
            ud_align_df=self.aligned_ud_df,
            lang=self.args.lang
        )

        # Save answers to disk
        self.verb_qasem_df_path = self.raw_output_dir / f"target-QASRL-{self.num_start}-{self.num_end}.csv"
        self.verb_qasem_df.to_csv(self.verb_qasem_df_path, index=False)

        print(f"Saved Verb QASem to: {self.verb_qasem_df_path}")


    def generate_nominalization_data(self):
        print("Generating nominalization questions and answers...")

        if self.verb_questions_df is None:
            verb_questions_df_path = {self.raw_output_dir} / f"QASRL-questions-{self.num_start}-{self.num_end}.csv"
            self.verb_questions_df = pd.read_csv(verb_questions_df_path, dtype={'sent_id': str})

        # Step 1: Create nominalization questions
        self.nom_questions_df = qa_nom.create_nominalization_questions(
            df=self.verb_questions_df,
            model=self.llm_model,
            tokenizer=self.llm_tokenizer,
            lang=self.args.lang,
        )

        nom_questions_df_path = self.raw_output_dir / f"QANom-questions-{self.num_start}-{self.num_end}.csv"
        self.nom_questions_df.to_csv(nom_questions_df_path, index=False)
        print(f"Saved nominalization questions to: {nom_questions_df_path}")

        # Step 2: Generate answers
        if self.aligned_ud_df is None:
            aligned_path = self.raw_output_dir / "UD-tokenized-translated-aligned.csv"
            self.aligned_ud_df = pd.read_csv(aligned_path, dtype={'sent_id': str})

        self.nom_qasem_df = answers.get_answers(
            df=self.nom_questions_df,
            ud_align_df=self.aligned_ud_df,
            lang=self.args.lang
        )
        nom_qasem_df_path = self.raw_output_dir / f"target-QANom-{self.num_start}-{self.num_end}.csv"
        self.nom_qasem_df.to_csv(nom_qasem_df_path, index=False)
        print(f"Saved nominalization QASem data to: {nom_qasem_df_path}")
        
    
    def merge_verb_and_nom_qasem(self):
        """
        Merge QASRL (verbal) and QANom (nominal) data into a unified QASem dataset.
        Keeps only the relevant columns and tags the source and type explicitly.
        """

        def rename_columns(df):
            df = df.drop(columns=["answers"])
            new_column_names = {
                'sent_id': 'sent_id',
                'tok_target_sentence': 'sentence',
                'chosen_predicate': 'predicate',
                'target_predicate_idx': 'predicate_idx',
                'translate_question': 'questions',
                'new_aligned_target_answers': 'answers',
            }
            df = df.rename(columns=new_column_names)
            return df

        def keep_columns_for_dataset(df, col_list, type_value):
            df = df[col_list].copy()
            df["type"] = type_value
            return df

        def merge_qasrl_qanom_dfs(df_srl, df_nom):
            merged_df = pd.concat([df_srl, df_nom], ignore_index=True)
            merged_df = merged_df.sort_values(by=["sent_id", "predicate_idx"])
            return merged_df

        print("Preparing QASRL and QANom data for merging...")

        if self.verb_qasem_df is None:
            verb_qasem_path = self.raw_output_dir / f"target-QASRL-{self.num_start}-{self.num_end}.csv"
            self.verb_qasem_df = pd.read_csv(verb_qasem_path, dtype={'sent_id': str})
            
        if self.nom_qasem_df is None:
            nom_qasem_path = self.raw_output_dir / f"target-QANom-{self.num_start}-{self.num_end}.csv"
            self.nom_qasem_df = pd.read_csv(nom_qasem_path, dtype={'sent_id': str})

        col_list = ["sent_id", "sentence", "predicate", "predicate_idx", "questions", "answers"]

        # Rename, filter, and label
        qasrl_df = rename_columns(self.verb_qasem_df)
        qasrl_df = keep_columns_for_dataset(qasrl_df, col_list, type_value="verb")

        qanom_df = rename_columns(self.nom_qasem_df)
        qanom_df = keep_columns_for_dataset(qanom_df, col_list, type_value="noun")

        # Merge
        merged_df = merge_qasrl_qanom_dfs(qasrl_df, qanom_df)
        self.combined_qasem_df = merged_df.reset_index(drop=True)

        # Save
        merged_path = self.final_dataset_dir / f"QASem-{self.num_start}-{self.num_end}.csv"
        self.combined_qasem_df.to_csv(merged_path, index=False)
        print(f"Merged dataset saved to: {merged_path}")


if __name__ == "__main__":
    args = parse_arguments()
    pipeline = QASemProjection(args)

    if args.preprocessing:
        pipeline.preprocess()

    if not args.skip_parsing:
        pipeline.run_parser()

    pipeline.project_to_target()

    pipeline.generate_questions()
    
    pipeline.generate_answers()
        
    pipeline.generate_nominalization_data()
    
    pipeline.merge_verb_and_nom_qasem()

    print("QASem projection pipeline completed successfully!")
    
    

