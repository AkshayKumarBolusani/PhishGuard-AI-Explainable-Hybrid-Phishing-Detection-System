# PhishGuard AI — Public Benchmark Evaluation Report

**Date:** 2026-10-18
**Status:** measured, not simulated. Raw results: `evaluation/benchmark_results.json`

## Benchmark
**Phishing Email Curated Datasets**, Zenodo DOI [10.5281/zenodo.8339691](https://doi.org/10.5281/zenodo.8339691) (CC-BY-4.0),
version v1 (published 2023-09-13), via the byte-identical HuggingFace mirror
`kudzaiprichard/aura-phishing-email-corpus`.
All 5 CSVs were MD5-verified against the Zenodo-published checksums on 2026-10-19:

| File | MD5 (Zenodo v1) |
|---|---|
| `TREC_07.csv` | `e5a5ae0de1580965191cb32806dc0dae` |
| `CEAS_08.csv` | `1f0d59191eec892a709995d48cd8decb` |
| `Nazario_5.csv` | `45db8330ea4aabbf72f5199949ae03e5` |
| `Nigerian_5.csv` | `edfbbb89c40e7447f47867bcc82e72f9` |
| `SpamAssasin.csv` | `d921e0b2333bfaa058bd38193e6b3fbd` |

The collection is curated for phishing-email research (see Champa et al., ISDFS 2024
and ICMI 2024), but the **label semantics differ per corpus** — the positive class
is *spam* for the three spam-track corpora, *phishing* for Nazario_5, and
*advance-fee fraud* for Nigerian_5 (verified against the source tracks and by
inspecting labeled examples). Scores below are reported against each corpus's own
positive class; they are not a single pooled "phishing detection" score.

| Corpus | n | Positive | Legitimate | Positive class means |
|---|---|---|---|---|
| TREC_07 (TREC 2007 spam track) | 53,757 | 29,399 | 24,358 | spam |
| CEAS_08 (CEAS 2008 challenge) | 39,154 | 21,842 | 17,312 | spam |
| Nazario_5 (Nazario phishing + legit) | 3,065 | 1,565 | 1,500 | phishing |
| Nigerian_5 (Nigerian fraud + legit) | 6,331 | 3,332 | 2,999 | advance-fee fraud |
| SpamAssasin (SpamAssassin corpus) | 5,809 | 1,718 | 4,091 | spam |

## Protocol
- Stratified 5-fold cross-validation, `random_state=42`, **identical splits for all models**.
- TF-IDF vectorizer fit on the train fold only (no leakage).
- Metrics computed on pooled out-of-fold predictions: accuracy, precision / recall / F1
  on the **positive class** (corpus-specific semantics — see table above), plus macro F1.
- Binary labels (1 = positive class, 0 = legitimate). The repo's `suspicious` class does not
  exist in public corpora. Transformer layer excluded (configurable/untrained in the repo).
- The 130-email demo set was **not** used anywhere in this evaluation.

## Models
1. **pilfer_rf** — PILFER-style baseline: 10 hand-crafted URL/HTML heuristic features
   (IP-literal URL, URL/domain counts, non-matching anchor vs href, `@` in URL, subdomain
   depth, HTML form, JavaScript, max URL length, HTTPS ratio) + RandomForest(100).
   Reimplementation of the Fette et al. 2007 idea; domain-age/WHOIS and SpamAssassin-output
   features omitted (no network access). Labeled as PILFER-*style*, not PILFER verbatim.
2. **tfidf_lr** — the repo's exact ML config: TF-IDF (10k features, 1–2 grams, min_df=2,
   max_df=0.95, sublinear TF) + LogisticRegression (C=1.0, balanced).
3. **tfidf_svm** — same TF-IDF + LinearSVC (balanced).
4. **phishguard_hybrid** — the repo's pipeline, faithfully replicated: the actual
   `RuleEngine` class imported from `backend/app/ai/rule_engine.py` (29 rules),
   combined as `0.35 * P_rule(phishing) + 0.65 * mean(P_LR, P_RF)` per the repo's
   `FALLBACK_WEIGHTS`; phishing predicted at ≥ 0.5.

## Results

### TREC_07 (n=53,757)
| Model | Accuracy | Precision | Recall | F1 (pos.) | F1 macro |
|---|---|---|---|---|---|
| pilfer_rf | 0.8406 | 0.7906 | 0.9638 | 0.8687 | 0.8330 |
| tfidf_lr | 0.9938 | 0.9914 | 0.9972 | 0.9943 | 0.9937 |
| tfidf_svm | **0.9960** | 0.9948 | **0.9979** | **0.9964** | **0.9960** |
| phishguard_hybrid | 0.9846 | **0.9962** | 0.9756 | 0.9858 | 0.9845 |

### CEAS_08 (n=39,154)
| Model | Accuracy | Precision | Recall | F1 (pos.) | F1 macro |
|---|---|---|---|---|---|
| pilfer_rf | 0.7934 | 0.9493 | 0.6650 | 0.7822 | 0.7928 |
| tfidf_lr | 0.9950 | 0.9963 | 0.9947 | 0.9955 | 0.9949 |
| tfidf_svm | **0.9973** | 0.9977 | **0.9975** | **0.9976** | **0.9973** |
| phishguard_hybrid | 0.9783 | **0.9989** | 0.9621 | 0.9802 | 0.9781 |

### Nazario_5 (n=3,065)
| Model | Accuracy | Precision | Recall | F1 (pos.) | F1 macro |
|---|---|---|---|---|---|
| pilfer_rf | 0.7214 | 0.6556 | 0.9572 | 0.7782 | 0.7018 |
| tfidf_lr | 0.9905 | 0.9929 | 0.9885 | 0.9907 | 0.9905 |
| tfidf_svm | **0.9954** | 0.9968 | **0.9942** | **0.9955** | **0.9954** |
| phishguard_hybrid | 0.9361 | **0.9978** | 0.8767 | 0.9333 | 0.9359 |

### Nigerian_5 (n=6,331)
| Model | Accuracy | Precision | Recall | F1 (pos.) | F1 macro |
|---|---|---|---|---|---|
| pilfer_rf | 0.6636 | 0.6240 | 0.9079 | 0.7396 | 0.6322 |
| tfidf_lr | 0.9926 | **0.9997** | 0.9862 | 0.9929 | 0.9926 |
| tfidf_svm | **0.9953** | **0.9997** | **0.9913** | **0.9955** | **0.9953** |
| phishguard_hybrid | 0.9788 | **0.9997** | 0.9601 | 0.9795 | 0.9788 |

### SpamAssasin (n=5,809)
| Model | Accuracy | Precision | Recall | F1 (pos.) | F1 macro |
|---|---|---|---|---|---|
| pilfer_rf | 0.8167 | 0.6470 | 0.8364 | 0.7296 | 0.7955 |
| tfidf_lr | 0.9840 | 0.9662 | 0.9802 | 0.9731 | 0.9809 |
| tfidf_svm | **0.9904** | 0.9815 | **0.9860** | **0.9837** | **0.9884** |
| phishguard_hybrid | 0.9496 | **0.9850** | 0.8423 | 0.9081 | 0.9367 |

## Honest reading of the results
1. **The hybrid does NOT beat TF-IDF + SVM on F1 on any corpus.** Pure TF-IDF models
   score 0.97–1.00 F1 across all five corpora. This is reported as measured — no
   cherry-picking, no SOTA claim for the hybrid on accuracy.
2. **What the hybrid does add:** the highest or near-highest **precision** on every
   corpus (0.9850–0.9997) — i.e., the fewest false alarms — plus deterministic,
   explainable rule signals and per-indicator explanations. In SOC triage, false
   positives are expensive analyst time, so precision-first behavior is a legitimate
   systems contribution, framed as such. This precision advantage is an empirical
   result on these corpora and splits, not proof of superiority in operational
   SOC environments.
3. **Recall cost is real:** on Nazario_5 (0.8767) and SpamAssassin (0.8423) the rule
   layer's conservatism drags recall down. This is a documented trade-off, not hidden.
4. **PILFER-style baseline behaves as expected:** high recall (0.84–0.96), lower
   precision — heuristics catch a lot but cry wolf. It is a fair classical baseline.
5. **Demo-130 numbers retired from any accuracy claim:** the old
   "LR F1 0.83 / RF F1 0.85" figures were 5-fold CV on a 130-email demonstration set
   and are now labeled **pipeline-validation only** everywhere. They are not benchmark
   accuracy and are never presented as such.

## Duplicate sensitivity (2026-10-19)
Exact duplicates on normalized subject+body are rare (≤0.14% per corpus, none
with conflicting labels). A full rerun with duplicates removed **before** the
stratified split (`benchmark_dedup.py`, identical settings otherwise) kept
53,683 / 39,145 / 3,063 / 6,315 / 5,809 messages per corpus. Largest per-model
F1 movement: **0.0029** (Nazario_5 hybrid, 0.9333 → 0.9362); all other deltas
≤ 0.0012; SpamAssassin bit-identical. Best-precision and best-F1 orderings
unchanged on all five corpora. Raw: `evaluation/benchmark_results_dedup.json`.
Duplicates do not drive the findings.

## Limitations
- Binary corpora: the repo's 3-class `suspicious` category could not be evaluated.
- Transformer (DistilBERT) layer not evaluated — it is configurable/untrained in the repo.
- Rule engine thresholds are the repo's defaults; no threshold tuning was done (tuning on
  the benchmark would be legitimate future work — report it if you do it).
- SOC triage-time impact is **not measured** — see `SOC_TRIAGE_PROTOCOL.md` (protocol
  defined, pilot pending; needs real Wazuh alerts + a timed analyst run).

## Reproduction
Exact environment (pinned, 2026-10-19): `numpy==2.5.4`, `pandas==3.0.6`,
`scikit-learn==1.9.1`, `scipy==1.18.1`, Python 3.12.

```bash
python3 -m venv .venv && .venv/bin/pip install "numpy==2.5.4" "pandas==3.0.6" "scikit-learn==1.9.1" "scipy==1.18.1"
# put the five MD5-verified CSVs in evaluation/data/, then from the repo root:
.venv/bin/python evaluation/benchmark.py
```

`benchmark.py` re-runs everything (stratified 5-fold CV, `random_state=42`,
identical splits) and writes fresh results to `evaluation/benchmark_results.json`.
Datasets: `data/*.csv` (MD5-verified against the Zenodo v1 checksums listed above).
Rule engine imported verbatim from `backend/app/ai/rule_engine.py`.
A deduplicated-sensitivity rerun lives in `benchmark_dedup.py`
(removes exact duplicates on normalized subject+body *before* splitting).
