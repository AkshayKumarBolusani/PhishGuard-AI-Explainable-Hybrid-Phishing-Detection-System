# Limitations

This document preserves the limitations of the PhishGuard evaluation as
stated in the paper (`paper/phishguard.tex`) and the benchmark report
(`evaluation/BENCHMARK_REPORT.md`). They are disclosed here so that the
results are not read more broadly than the evidence supports.

## Evaluation scope

- **Binary evaluation only.** Every corpus is binary (label 1 = positive
  class, 0 = legitimate). The system's `suspicious` class exists in the
  pipeline but is not exercised or evaluated anywhere in the benchmark.
- **Positive-class semantics are corpus-specific.** Three corpora label
  spam vs legitimate, one labels phishing vs legitimate, and one labels
  advance-fee fraud vs legitimate (see `label_mapping.md`). Results describe
  each corpus separately; they are not a pooled phishing-detection claim.
- **No cross-dataset evaluation.** Each corpus is evaluated with
  within-corpus 5-fold cross-validation only. There is no train-on-one-
  corpus / test-on-another experiment, so the results say nothing about
  transfer between corpora.
- **Historical English-language corpora.** The largest corpora (TREC 2007,
  CEAS 2008, SpamAssassin) are early-2000s, English-language spam tracks.
  They do not represent today's phishing tactics, languages, or channels.
  Good performance on these historical datasets is not evidence of
  effectiveness against current real-world phishing attacks.

## Model configuration

- **DistilBERT layer untrained and excluded.** The pipeline has a
  configurable DistilBERT transformer layer, but it is untrained in the
  repository and was excluded from every reported benchmark result. All
  results reflect the 29-rule engine plus the TF-IDF logistic-regression /
  random-forest ensemble only.
- **Ensemble weights are shipped defaults, not tuned.** The hybrid's
  0.35 (rules) / 0.65 (ML) weighting is the repository's `FALLBACK_WEIGHTS`
  default. The weights, the 0.5 decision threshold, and the rule thresholds
  were not tuned on the benchmark corpora. Tuning on the benchmark would be
  legitimate future work — it has not been done.
- **Baselines have known simplifications.** The PILFER-style random-forest
  baseline is a reimplementation of the Fette et al. 2007 idea: domain-age/
  WHOIS and SpamAssassin-output features are omitted (no network access at
  benchmark time). The TF-IDF classifiers are deliberately simple
  (10k features, 1–2 grams, C=1.0 logistic regression, LinearSVC) — they are
  the repository's shipped configuration, not tuned competitors.

## Data caveats

- **Regex rules can be evaded.** The 29 rules are deterministic
  regular-expression indicators. Adversarial rewording, obfuscation, or
  novel templates can bypass them; no claim is made about adversarial
  robustness.
- **Near-duplicate templates.** Beyond exact duplicates, these corpora
  contain near-duplicate message templates (e.g. repeated spam campaigns).
  Only exact duplicates were audited and tested (see below); near-duplicate
  leakage is a known residual caveat of template-heavy spam corpora.
- **Duplicate sensitivity measured, not assumed.** Exact duplicates
  (normalized subject+body) were rare (≤0.14% per corpus, none with
  conflicting labels). A full rerun with duplicates removed *before* the
  stratified split found a maximum per-model F1 movement of **0.0029**
  (Nazario_5 hybrid, 0.9333 → 0.9362); all other deltas ≤ 0.0012;
  SpamAssassin was bit-identical; best-precision and best-F1 orderings were
  unchanged on all five corpora. Raw: `evaluation/benchmark_results_dedup.json`.
  The findings are not driven by duplicates, but near-duplicate templates
  remain unmeasured.

## Operational claims not made

- **No measured analyst time savings.** The rule reports are a system
  feature (explanations per indicator), but the benchmark does not measure
  whether they improve analyst decisions or reduce triage time. A protocol
  for such a study (`SOC_TRIAGE_PROTOCOL.md`) is defined; the pilot has not
  been run.
- **No SOC efficacy claim.** The hybrid's precision advantage over TF-IDF+SVM
  on these corpora and splits is an empirical result, not proof of
  operational SOC superiority.
- **No SOTA claim.** TF-IDF+SVM achieves the best F1 on all five corpora;
  the hybrid does not beat it on F1 anywhere. This is reported as measured.
