# Mike's Data Science & Artificial Intelligence Portfolio

A repository of data science projects analysing traffic congestion patterns, predicting employee engagement strategies, triaging social media toxicity via sentiment analysis, and modelling title book behaviour in the publishing industry. I am a learning and development and creative professional, with a BFA(Graphic Design) and PGDE, with advanced skills in data science and AI. These projects reflect my technical proficiency in Python and fluency with data visualisation, as well as my inquiry into real-world systems and datasets. 

<i>Many thanks to Dr Chaitanya Rao, Institute of Data, for his validation of my skills and expertise reflected through these projects.</i>

---

## Projects

### [Project 1 — Bus Passenger Load Along Singapore's NEL Corridor](./1_traffic-patterns/)
**APIs · Geospatial · EDA · Data Storytelling**

Analysed bus passenger load patterns at stops in the Kovan–Serangoon–Woodleigh region, using real-time May 2026 data from the LTA DataMall API. Framed against Singapore's Land Transport Master Plan 2040 Walk-Cycle-Ride goals.

---

### [Project 2 — Predicting Return-to-Office Responses](./2_workforce-analytics/)
**Classification · Logistic Regression · Imbalanced Data · Workforce Analytics**

Built a multinomial classification model to predict employee responses to return-to-office mandates (Quit / Seek WFH / Comply), using the Global Survey of Working Arrangements (G-SWA) Wave 2 dataset (~23,800 respondents, 25 countries).

---

### [Project 3 — Toxic Comment Classification](./3_toxicity-sentiment-analysis/)
**NLP · TF-IDF · Classical ML · DistilBERT · Content Moderation**

Engineered an end-to-end NLP pipeline classifying toxic comments from the `google/civil_comments` dataset (150k-row stratified sample from ~902k). Compared 12 classical sklearn pipelines against a fine-tuned DistilBERT transformer model.

---

### [Project 4 — Modelling Book Title Revenue and Lifecycle](./4_modelling-publishing-title-behaviour/)
**Time Series · Decay Modelling · ML Regression · Real-World Client Engagement**

Architected a predictive modelling pipeline analysing a 180-month invoice register (94,872 lines) across three research tracks: demand mix, title lifecycle decay, and revenue exposure, in collaboration with a client. 

---

## Tech Stack

| Category | Tools |
|---|---|
| Languages | Python 3 |
| Data | pandas, NumPy |
| Visualisation | Matplotlib, Seaborn, Folium |
| Machine Learning | scikit-learn |
| NLP | spaCy, Hugging Face Transformers (DistilBERT) |
| Deep Learning | PyTorch |
| Time Series | statsmodels (SARIMA, Holt-Winters) |
| Environment | Jupyter Notebook, Google Colab |
| APIs | LTA DataMall, OneMap |

---

## Setup

```bash
git clone https://github.com/michaelee90/data-science-portfolio.git
cd data-science-portfolio
pip install -r requirements.txt
```

> **Note:** Datasets and API keys are not included. See each project's README for data access instructions.

---

## About Mike

Hi there! I'm a creative learning and development professional branching into data science and analytics. My background in graphic design, education and civil service shapes how I approach problem-solving: making data-derived actionable insights clear for public good.

- Portfolio: [mikeee.co](https://www.mikeee.co)
- GitHub: [@michaelee90](https://github.com/michaelee90)
