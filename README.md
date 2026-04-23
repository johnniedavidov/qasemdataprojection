# QASem Projection Pipeline

This repository contains an end-to-end pipeline for projecting QA-based Semantic Representations (QASem), including both verbal (QASRL) and nominal (QANom) predicates, into target languages via translation and alignment techniques.

## Overview

The pipeline supports:
- Processing Universal Dependencies (UD) `.conllu` files.
- Translating and aligning sentences.
- Running an English QASem parser.
- Generating translated QA pairs for verbs and nominals.
- Producing final datasets in the target language with full QASem annotations.

---

## 🛠️ Requirements

Before running the pipeline, make sure you have installed all dependencies:

```bash
pip install -r requirements.txt
```

(Or alternatively, use `environment.yml` if using conda.)

---

## 🚀 Running The Dataset Creation Pipeline

To run the pipeline end-to-end:

```bash
python run_dataset_pipeline.py \
  --lang Ru \
  --ud_path source_ud_data/russian/ru_taiga-ud-dev.conllu \
  --source taiga-dev \
  --preprocessing
```

### Arguments

| Argument            | Type    | Required | Description |
|---------------------|---------|----------|-------------|
| `--lang`            | string  | ✅        | Target language code: `He`, `Ru`, or `Fr`. |
| `--ud_path`         | path    | ✅        | Path to the UD `.conllu` file. |
| `--source`          | string  | ✅        | Dataset source name (e.g., `wiki`, `htb`, `gsd`, `taiga`). |
| `--preprocessing`   | flag    | ❌        | If set, will preprocess and realign the UD file. |
| `--skip_parsing`    | flag    | ❌        | If set, skips the English QASem parsing step. |
| `--num_start_rows`  | int     | ❌        | Start index for processing rows. Default: 0. |
| `--num_end_rows`    | int     | ❌        | End index (exclusive) for processing. Default: `start + 100`. |

---

## 🧾 Output Format

The final output CSV is saved under:

```
datasets/<LANG>_<SOURCE>/QASem-<START>-<END>.csv
```

It includes the following columns:

- `sent_id`: Sentence identifier.
- `sentence`: Target language sentence.
- `predicate`: Predicate word in the sentence.
- `predicate_idx`: Index of the predicate.
- `questions`: Translated natural language question.
- `answers`: Target language answer span(s).
- `type`: `verb` (QASRL) or `noun` (QANom).

---

## 🧪 Example Output

| sent_id | sentence | predicate | predicate_idx | questions | answers | type |
|---------|----------|-----------|----------------|-----------|---------|------|
| ru_taiga-1 | Он пошёл домой. | пошёл | 1 | Кто пошёл? | Он | verb |

---

## ⚙️ Requirements

Make sure to install the dependencies (e.g., using `requirements.txt` or `conda` environment). Recommended libraries include:

- `transformers`
- `pandas`
- `spacy`
- `simalign`
- `torch`

---

## 🛠 Notes

- Designed for extensibility: add new languages by defining suitable translation and LLM models.
- Built-in support for Hebrew, Russian, and French.
- Use GPU for best performance.

---

## 📝 Citation

If you use this pipeline in your work, please cite:

```
@inproceedings{davidov-etal-2026-effective,
    title = "Effective {QA}-Driven Annotation of Predicate{--}Argument Relations Across Languages",
    author = "Davidov, Jonathan  and
      Slobodkin, Aviv  and
      Klein, Shmuel Tomi  and
      Tsarfaty, Reut  and
      Dagan, Ido  and
      Klein, Ayal",
    editor = "Demberg, Vera  and
      Inui, Kentaro  and
      Marquez, Llu{\'i}s",
    booktitle = "Proceedings of the 19th Conference of the {E}uropean Chapter of the {A}ssociation for {C}omputational {L}inguistics (Volume 1: Long Papers)",
    month = mar,
    year = "2026",
    address = "Rabat, Morocco",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2026.eacl-long.112/",
    doi = "10.18653/v1/2026.eacl-long.112",
    pages = "2484--2502",
    ISBN = "979-8-89176-380-7",
    abstract = "Explicit representations of predicate-argument relations form the basis of interpretable semantic analysis, supporting reasoning, generation, and evaluation. However, attaining such semantic structures requires costly annotation efforts and has remained largely confined to English. We leverage the Question-Answer driven Semantic Role Labeling (QA-SRL) framework {---} a natural-language formulation of predicate-argument relations {---} as the foundation for extending semantic annotation to new languages. To this end, we introduce a cross-linguistic projection approach that reuses an English QA-SRL parser within a constrained translation and word-alignment pipeline to automatically generate question-answer annotations aligned with target-language predicates. Applied to Hebrew, Russian, and French {---} spanning diverse language families {---} the method yields high-quality training data and fine-tuned, language-specific parsers that outperform strong multilingual LLM baselines (GPT-4o, LLaMA-Maverick). By leveraging QA-SRL as a transferable natural-language interface for semantics, our approach enables efficient and broadly accessible predicate-argument parsing across languages."
}
```

---

## 🤝 Acknowledgements

This work was developed as part of a master's thesis under the supervision of Prof. Ido Dagan and Dr. Ayal Klein.

---

## 📁 Folder Structure

```
.
├── run_dataset_pipeline.py
├── scripts/
│   ├── preprocess.py
│   ├── alignment.py
│   ├── projection.py
│   ├── qa/
│   └── utils/
├── preprocessed_data/
├── generated_qasem_data/
└── source_ud_data/
```

---

## 🔒 License

MIT License
