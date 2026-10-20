"""
PhishGuard AI — public benchmark evaluation (DEDUP-SENSITIVITY VARIANT).

Identical to benchmark.py except: exact duplicates (normalized subject+body)
are removed BEFORE the stratified split, so no duplicate message can appear
in both train and test folds of the same run.

Corpora: Phishing Email Curated Datasets, Zenodo DOI 10.5281/zenodo.8339691
(CC-BY-4.0), via byte-identical HF mirror kudzaiprichard/aura-phishing-email-corpus
(MD5-verified against Zenodo-published checksums).

Models (all on identical stratified 5-fold splits, random_state=42):
 1. pilfer_rf      — PILFER-style: 10 hand-crafted URL/HTML heuristic features + RF.
                      Reimplementation of the Fette et al. 2007 idea; domain-age/WHOIS
                      and SpamAssassin-output features omitted (no network access).
 2. tfidf_lr       — repo's exact config: TF-IDF(10k, 1-2gram) + LogisticRegression.
 3. tfidf_svm      — same TF-IDF + LinearSVC (balanced).
 4. phishguard_hybrid — repo's pipeline adapted to binary labels:
                      0.35 * rule_engine P(phishing) + 0.65 * mean(LR, RF P(phishing)).
                      Rule engine imported verbatim from backend/app/ai/rule_engine.py.
                      Transformer layer excluded (configurable/untrained in repo).
                      "Suspicious" class absent from public corpora (binary labels).

Metrics: accuracy, precision, recall, F1 on the phishing class + macro F1,
reported as 5-fold mean ± std. Demo-130 numbers are NOT used here.
"""
import json
import re
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, f1_score, precision_score,
                             recall_score)
from sklearn.model_selection import StratifiedKFold
from sklearn.svm import LinearSVC

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
from app.ai.rule_engine import RuleEngine  # noqa: E402  (pure-python, no deps)

BASE = Path(__file__).parent.parent
DATA = BASE / "data"
OUT = Path(__file__).parent
OUT.mkdir(exist_ok=True)

CORPORA = {
    "TREC_07": "TREC 2007 spam track (53,757 emails)",
    "CEAS_08": "CEAS 2008 challenge (39,154 emails)",
    "Nazario_5": "Nazario phishing + legitimate (3,065 emails)",
    "Nigerian_5": "Nigerian fraud + legitimate (6,331 emails)",
    "SpamAssasin": "SpamAssassin corpus (5,809 emails)",
}

URL_RE = re.compile(r"https?://[^\s<>'\"]+|www\.[^\s<>'\"]+", re.IGNORECASE)
HREF_RE = re.compile(r'href\s*=\s*["\']([^"\']+)["\']', re.IGNORECASE)
ANCHOR_RE = re.compile(r"<a\s[^>]*>(.*?)</a>", re.IGNORECASE | re.DOTALL)
IP_RE = re.compile(r"https?://\d{1,3}(\.\d{1,3}){3}")
TAG_STRIP = re.compile(r"<[^>]+>")


def host_of(url: str) -> str:
    u = re.sub(r"^https?://", "", url, flags=re.IGNORECASE).split("/")[0]
    return u.split("@")[-1].split(":")[0].lower()


def pilfer_style_features(texts):
    """10 hand-crafted URL/HTML heuristic features (PILFER-style, reimplemented)."""
    feats = []
    for t in texts:
        urls = URL_RE.findall(t)
        hosts = [host_of(u) for u in urls]
        hrefs = HREF_RE.findall(t)
        anchors = ANCHOR_RE.findall(t)
        # non-matching: anchor text looks like a URL but differs from href host
        nonmatch = 0
        for a, h in zip(anchors, hrefs):
            a_clean = TAG_STRIP.sub("", a).strip().lower()
            if re.match(r"(https?://|www\.)", a_clean):
                if host_of(a_clean) != host_of(h):
                    nonmatch = 1
                    break
        tl = t.lower()
        feats.append([
            1 if any(IP_RE.search(u) for u in urls) else 0,          # ip_url
            len(urls),                                               # n_urls
            len(set(hosts)),                                         # n_domains
            nonmatch,                                                # nonmatching_url
            1 if any("@" in u for u in urls) else 0,                 # at_in_url
            max([h.count(".") for h in hosts] + [0]),               # max_dots
            1 if ("<form" in tl or "<input" in tl) else 0,           # has_form
            1 if ("<script" in tl or "javascript:" in tl) else 0,    # has_js
            max([len(u) for u in urls] + [0]),                      # max_url_len
            sum(1 for u in urls if u.lower().startswith("https")) / max(len(urls), 1),  # https_ratio
        ])
    return np.array(feats, dtype=float)


def load_corpus(name):
    df = pd.read_csv(DATA / f"{name}.csv", usecols=["sender", "subject", "body", "label"])
    df["subject"] = df["subject"].fillna("")
    df["body"] = df["body"].fillna("")
    df["sender"] = df["sender"].fillna("")
    texts = (df["subject"] + " " + df["body"]).tolist()
    full = ("Subject: " + df["subject"] + "\n\n" + df["body"]).tolist()
    y = df["label"].astype(int).to_numpy()
    return texts, full, y


def rule_phishing_proba(rule_engine, full_texts):
    """P(phishing) from the repo's rule engine (deterministic, no training)."""
    probs = np.zeros(len(full_texts))
    for i, t in enumerate(full_texts):
        matches = rule_engine.analyze(t)
        _, p = rule_engine.classify(matches)
        probs[i] = p["phishing"]
    return probs


def evaluate_corpus(name, rule_engine):
    texts, full_texts, y = load_corpus(name)
    print(f"[{name}] n={len(y)}, phishing={int(y.sum())}", flush=True)
    # --- dedup-sensitivity: drop exact duplicates before splitting ---
    import hashlib as _hl
    _seen, _keep = {}, []
    for _i, _t in enumerate(texts):
        _h = _hl.md5(_t.lower().strip().encode("utf-8", "ignore")).hexdigest()
        if _h not in _seen:
            _seen[_h] = _i
            _keep.append(_i)
    _keep = np.array(_keep)
    print(f"[{name}] dedup kept {len(_keep)}/{len(y)}", flush=True)
    texts = [texts[i] for i in _keep]
    full_texts = [full_texts[i] for i in _keep]
    y = y[_keep]

    t0 = time.time()
    rule_proba = rule_phishing_proba(rule_engine, full_texts)
    print(f"[{name}] rule engine done in {time.time()-t0:.0f}s", flush=True)

    t0 = time.time()
    X_heur = pilfer_style_features(texts)
    print(f"[{name}] heuristic features done in {time.time()-t0:.0f}s", flush=True)

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    preds = {m: [] for m in ["pilfer_rf", "tfidf_lr", "tfidf_svm", "phishguard_hybrid"]}
    trues = []

    for fold, (tr, te) in enumerate(skf.split(texts, y)):
        t0 = time.time()
        y_tr, y_te = y[tr], y[te]
        trues.append(y_te)

        # 1. PILFER-style RF on heuristic features
        rf_h = RandomForestClassifier(n_estimators=100, class_weight="balanced",
                                      random_state=42, n_jobs=-1)
        rf_h.fit(X_heur[tr], y_tr)
        preds["pilfer_rf"].append(rf_h.predict(X_heur[te]))

        # shared TF-IDF fit on train fold only (no leakage)
        vec = TfidfVectorizer(max_features=10000, ngram_range=(1, 2), min_df=2,
                              max_df=0.95, strip_accents="unicode", sublinear_tf=True)
        Xtr = vec.fit_transform([texts[i] for i in tr])
        Xte = vec.transform([texts[i] for i in te])

        # 2. TF-IDF + LR (repo config)
        lr = LogisticRegression(max_iter=1000, class_weight="balanced", C=1.0)
        lr.fit(Xtr, y_tr)
        p_lr = lr.predict_proba(Xte)[:, 1]
        preds["tfidf_lr"].append((p_lr >= 0.5).astype(int))

        # 3. TF-IDF + linear SVM
        svm = LinearSVC(class_weight="balanced", max_iter=3000)
        svm.fit(Xtr, y_tr)
        preds["tfidf_svm"].append(svm.predict(Xte))

        # 4. PhishGuard hybrid: 0.35*rule + 0.65*mean(LR,RF)  (repo FALLBACK_WEIGHTS)
        rf = RandomForestClassifier(n_estimators=100, max_depth=12, min_samples_leaf=2,
                                    class_weight="balanced", n_jobs=-1, random_state=42)
        rf.fit(Xtr, y_tr)
        p_rf = rf.predict_proba(Xte)[:, 1]
        p_ml = (p_lr + p_rf) / 2.0
        p_hybrid = 0.35 * rule_proba[te] + 0.65 * p_ml
        preds["phishguard_hybrid"].append((p_hybrid >= 0.5).astype(int))

        print(f"[{name}] fold {fold+1}/5 done in {time.time()-t0:.0f}s", flush=True)

    y_true = np.concatenate(trues)
    results = {}
    for m, fold_preds in preds.items():
        p = np.concatenate(fold_preds)
        results[m] = {
            "accuracy": round(float(accuracy_score(y_true, p)), 4),
            "precision_phishing": round(float(precision_score(y_true, p, zero_division=0)), 4),
            "recall_phishing": round(float(recall_score(y_true, p, zero_division=0)), 4),
            "f1_phishing": round(float(f1_score(y_true, p, zero_division=0)), 4),
            "f1_macro": round(float(f1_score(y_true, p, average="macro", zero_division=0)), 4),
        }
    return {"corpus": name, "n": len(y), "n_phishing": int(y.sum()),
            "description": CORPORA[name], "results": results}


def main():
    rule_engine = RuleEngine()
    print(f"Rule engine loaded: {len(rule_engine.rules)} rules", flush=True)
    all_results = {"benchmark": "Phishing Email Curated Datasets, Zenodo DOI 10.5281/zenodo.8339691 (CC-BY-4.0)",
                   "mirror": "kudzaiprichard/aura-phishing-email-corpus (MD5-verified)",
                   "protocol": "stratified 5-fold CV, random_state=42, identical splits for all models",
                   "note": "DEDUP VARIANT: exact duplicates removed before splitting. Binary labels (1=positive, 0=legitimate); positive-class semantics are corpus-specific (see report). Repo 'suspicious' class absent. "
                           "Transformer layer excluded (configurable/untrained in repo). "
                           "Demo-130 numbers are pipeline-validation only and are NOT reported here.",
                   "corpora": []}
    for name in CORPORA:
        all_results["corpora"].append(evaluate_corpus(name, rule_engine))
        with open(OUT / "benchmark_results_dedup.json", "w") as f:
            json.dump(all_results, f, indent=2)
    print("Saved", OUT / "benchmark_results_dedup.json", flush=True)


if __name__ == "__main__":
    main()
