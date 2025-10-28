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
@misc{your_citation_here,
  title={Cross-Lingual QA-based Semantic Role Labeling},
  author={Davidov, Yonatan et al.},
  year={2025},
  note={Under Review}
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