# Label Mapping

All five corpora in the benchmark use binary labels:

- **1 = positive class**
- **0 = legitimate**

The catch — and the reason this document exists — is that "positive class"
does **not** mean the same thing in every corpus. The Zenodo collection is
named "Phishing Email Curated Datasets", but it repackages corpora from
different source tracks, and only one of them is actually a phishing corpus.
Label semantics were verified against the source tracks and by inspecting
labeled examples (see `evaluation/BENCHMARK_REPORT.md`).

## Per-corpus meaning of label 1

| Corpus | Label 1 (positive class) means | Label 0 means |
|---|---|---|
| TREC_07 | **spam** (TREC 2007 spam track) | legitimate |
| CEAS_08 | **spam** (CEAS 2008 challenge) | legitimate |
| Nazario_5 | **phishing** (Nazario phishing mail) | legitimate |
| Nigerian_5 | **advance-fee fraud** ("Nigerian" fraud mail) | legitimate |
| SpamAssasin | **spam** (SpamAssassin corpus) | legitimate |

So roughly 86% of the 108,116 benchmark messages carry spam-vs-legitimate
labels, not phishing-vs-legitimate labels.

## How the benchmark code uses the labels

- The benchmark (`evaluation/benchmark.py`) reads each corpus's `label`
  column directly and treats 1 as the positive class for precision, recall,
  and F1. No remapping is applied, and no corpus's labels are inverted.
- All metrics in `evaluation/benchmark_results.json` and
  `evaluation/benchmark_results_dedup.json` are computed against each corpus's
  **own** positive class, exactly as defined in the table above.

## Rules for interpreting results

1. **Never pool the corpora into a single "phishing" claim.** A score on
   TREC_07 is a spam-detection score; a score on Nazario_5 is a
   phishing-detection score; a score on Nigerian_5 is an advance-fee-fraud
   score. There is no single pooled "phishing detection" number, and none
   should be quoted.
2. **Name the corpus and its positive class when citing a metric.** E.g.
   "hybrid F1 0.9333 on Nazario_5 (positive = phishing)", not "phishing
   F1 0.93".
3. **The system's third class is not evaluated.** The PhishGuard pipeline
   also has a `suspicious` class, but it does not exist in these corpora —
   they are binary — so no benchmark result says anything about it.
4. The transformer (DistilBERT) layer is excluded from all reported results
   (configurable/untrained in the repository); the benchmark evaluates the
   rule engine plus the TF-IDF ML ensemble only.
