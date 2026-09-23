# Project 2 — Predicting Return-to-Office Responses

**Classification · Logistic Regression · Imbalanced Data · Workforce Analytics**

---

## Business Question

> *Will our workers return to physical office spaces?*

Specifically: can we predict how employees will respond to a return-to-office mandate — quit, seek a work-from-home role, or comply — based on their work arrangements, demographics, and preferences?

---

## Overview

This project builds a multinomial classification model on the **Global Survey of Working Arrangements (G-SWA) Wave 2** dataset — ~23,800 respondents across 25 countries. The key business application is a **flight-risk score**: identifying employees most likely to quit or job-seek in response to RTO policy changes, enabling HR teams to intervene proactively.

A significant modelling challenge was uncovered during EDA: a skip-logic design in the original survey produced a strong base-rate distortion in the target variable, requiring explicit handling before modelling.

---

## Key Findings

- **Final model:** Class-balanced multinomial logistic regression, chosen for interpretability and `predict_proba` support (required for flight-risk scoring). Balanced accuracy of **0.557** against a 0.333 majority-class baseline, and macro one-vs-rest ROC-AUC of **0.746**, ahead of Gaussian Naive Bayes and KNN (k=15)
- **Skip-logic discovery:** The survey's conditional branching inflated the "Comply" class, making naive accuracy misleading (83% base-rate trap)
- **Flight-risk output:** The model produces a per-employee probability across three RTO response classes, sorted into Lower / Moderate / Higher risk tiers. It ranks better than it labels: it catches over half of quitters, but Quit precision stays low (~6%), so P(Quit) is best used to prioritise retention conversations
- **Top predictors:** Current WFH days (coef −0.543) and commuting time (−0.113) push away from compliance; having no WFH experience (`wfh_missing`, +0.247) and older age (+0.153) push towards it
- **Robustness:** 5-fold CV scores sit close to the hold-out scores; dropping the family columns barely moves performance (−0.011 balanced accuracy); an ordinal logistic regression collapses on the Quit class, confirming the 83/15/2 imbalance, not model choice, is the main constraint

---

## Methods & Tools

| Step | Approach |
|---|---|
| Dataset | G-SWA Wave 2 (~23,800 rows, 25 countries) |
| Target | 3-class RTO response: Quit / WFH-seek / Comply |
| Preprocessing | Skip-logic and missing-data flags (`wfh_missing`, `family_missing`), dropping redundant and high-NaN columns, one-hot encoding of country and industry, stratified 80/20 split, `StandardScaler` fit on train only |
| Modelling | Majority-class baseline, Gaussian Naive Bayes, KNN (k=15), multinomial logistic regression (`class_weight="balanced"`); ordinal logistic regression (`mord`) as a robustness check |
| Evaluation | Balanced accuracy, macro-F1, macro one-vs-rest ROC-AUC, confusion matrices, stratified 5-fold CV; class-weight and P(Quit) threshold tuning; family-column drop test |
| Visualisation | Spearman correlation heatmap, feature-ranking and coefficient bar charts, stacked proportion bars, violin plots, ROC curves |

**Libraries:** `pandas`, `numpy`, `scikit-learn`, `mord`, `matplotlib`, `seaborn`

---

## Data

The G-SWA dataset is publicly available from [WFH Research](https://wfhresearch.com/gswadata/).

> The notebook reads `G-SWA.csv` from this folder. It is not included in this repo (large file); download it and save it here before running.

---

## Notebooks

- `Project 2 - Workforce Analytics.ipynb` — Main analysis notebook (137 cells, fully annotated, no error outputs)
