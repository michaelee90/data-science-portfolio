# Project 3 — Toxic Comment Classification

**NLP · TF-IDF · Classical ML Pipelines · DistilBERT · Content Moderation**

---

## Research Question

> *How toxic is a comment?*

Specifically: how accurately can we classify toxic comments in user-generated content, and what is the performance ceiling for classical bag-of-words approaches relative to a fine-tuned transformer model?

---

## Overview

End-to-end NLP pipeline for binary toxic comment classification, using the `google/civil_comments` dataset. The project is framed as a **content-moderation triage problem**: building an automated first-pass filter that flags likely-toxic content for human review.

Compared two paradigms: classical ML (12 pipelines across vectorisation and model combinations) against a fine-tuned DistilBERT transformer. Evaluation quantified the gap between sparse-feature approaches and contextual embeddings on a real-world moderation task.

---

## Key Results

| Model | Toxic-F1 | Macro-F1 |
|---|---|---|
| Best classical, light cleaning (`count_light` + LogReg) | 0.5698 | 0.7610 |
| Best classical, lemmatised (`count_lemma` + LogReg) | 0.5675 | 0.7591 |
| DistilBERT (fine-tuned, 20k rows, T4 GPU) | **0.6305** | **0.8010** |

DistilBERT lifted toxic-F1 by +0.061 (10.6% relative) over the best classical pipeline, despite training on 20,000 rows rather than ~120,000 — a meaningful gap in a real-world moderation context where false negatives carry real cost.

- **Lemmatisation does not pay off:** 17.72 extra minutes of preprocessing changed toxic-F1 by −0.002, so light cleaning is sufficient for bag-of-words models
- **Linear models hit a vocabulary ceiling:** all tuned LogReg and LinearSVC pipelines land between 0.556 and 0.570 toxic-F1; their strongest signals are overt insults, so they detect wording rather than intent
- **Errors lean towards false alarms:** the classical champion catches 73% of toxic comments, but 53% of its 3,649 flags are civil — P(toxic) is best used to rank a human moderation queue

---

## Methods

**Dataset:** Stratified 150k-row sample from `train-00000-of-00002.parquet` (902,437 comments; the first of two training files in `google/civil_comments`); binary label from `toxicity >= 0.5` (7.8% toxic). 375 comments left empty after cleaning were dropped, leaving 149,625 rows

**Preprocessing:**
- Stopword curation: NLTK stopwords tested by toxic/civil document-frequency lift; "yourself", "your", "very" and "nor" kept as class signals
- Two cleaning pipelines: light (NLTK `RegexpTokenizer` + curated stopwords) and lemmatisation (spaCy `en_core_web_sm`)
- ~22% vocabulary reduction from lemmatisation
- Frozen to `tokens_both.parquet` for reproducibility

**Classical ML:**
- 4 sparse matrices: `count_light`, `count_lemma`, `tfidf_light`, `tfidf_lemma`
- 3 classifiers: Logistic Regression, LinearSVC, Multinomial Naive Bayes
- 12 total pipelines, each tuned with GridSearchCV on toxic-F1 (`min_df` plus `C` or `alpha`), using one stratified 80/20 split shared by all models and DistilBERT
- Overfitting check: untuned pipelines compared on training vs test scores

**Transformer:**
- DistilBERT fine-tuned on 20k-row training subset (Colab T4 GPU, ~13 min)
- Results merged into comparison table via `bert_result.csv`

**Visualisation style:** Custom matplotlib house style — IBM Plex Sans, olive green `#8A9A5B`, maroon `#7B2D26`; figures auto-exported to `figures/` at 200 dpi. The font is loaded from a local `fonts/` folder (not included); without it, plots fall back to DejaVu Sans.

---

## Libraries

`pandas`, `numpy`, `pyarrow`, `scikit-learn`, `nltk`, `spacy`, `wordcloud`, `matplotlib`, `seaborn`; `torch`, `transformers`, `datasets` for DistilBERT fine-tuning (Colab)

---

## Data

The notebook reads `train-00000-of-00002.parquet` from this folder. Download it from the [`google/civil_comments`](https://huggingface.co/datasets/google/civil_comments) dataset on Hugging Face:
```python
from huggingface_hub import hf_hub_download
hf_hub_download(repo_id="google/civil_comments", repo_type="dataset",
                filename="data/train-00000-of-00002.parquet", local_dir=".")
```

> Large intermediate files (`tokens_both.parquet`, `bert_input.parquet`, `idx_*.npy`) and the source parquet are not included in this repo. Re-run the preprocessing cells to regenerate them. `bert_result.csv` (DistilBERT's scores, exported from Colab) is also not included, so the final leaderboard cells need it regenerated first.

---

## Notebooks

- `Project 3 - Toxicity Sentiment Analysis.ipynb` — Full pipeline: sampling → preprocessing → vectorisation → 12-model comparison → DistilBERT → final leaderboard

Screenshots embedded in the notebook's commentary callouts (keep them in this folder):
- `01_pipelineB_lemmatisation.png`, `02_pipelineB_lemmatisation_done.png` — lemmatisation run before and after
- `03_model-cv_results1.png`, `03_model-cv_results2.png`, `04_model-test_results1.png` — cross-validation and test results
- `05_BERT_tokeniser load.png`, `05_BERT_epoch and perf eval scores.png` — DistilBERT tokeniser load and training epochs on Colab

> **Note:** DistilBERT training requires a GPU. The notebook is designed to run training on Google Colab (T4 runtime) and merge results back locally via `bert_result.csv`.
