"""Train intent and sentiment classifiers on Gemini embeddings of the labeled set.
Usage: python data-pipeline/train.py
Writes: data-pipeline/models/{intent,sent}.joblib, data-pipeline/metrics.json, data-pipeline/embeddings.npz (cache)
Compares against the Gemini zero-shot baseline if data-pipeline/baseline.json exists (written by evaluate.py).
"""
import json
import sys
import time
from pathlib import Path

import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict

HERE = Path(__file__).parent
FIELDS = ("intent", "sent")


def cv_report(X, y, folds=5):
    """5-fold stratified cross-validated predictions -> (accuracy, macro_f1, text report)."""
    model = LogisticRegression(max_iter=2000, class_weight="balanced")
    pred = cross_val_predict(model, X, y, cv=StratifiedKFold(folds, shuffle=True, random_state=0))
    return accuracy_score(y, pred), f1_score(y, pred, average="macro"), classification_report(y, pred, zero_division=0)


def load_embeddings(rows):
    cache = HERE / "embeddings.npz"
    texts = [r["text"] for r in rows]
    if cache.exists():
        saved = np.load(cache, allow_pickle=False)
        if list(saved["texts"]) == texts:
            return saved["X"]
    sys.path.insert(0, str(HERE.parent / "backend"))
    from classifier import embed

    vecs = []
    for i in range(0, len(texts), 50):  # free tier: 100 embedded texts per minute
        if i:
            time.sleep(61)
        vecs += embed(texts[i : i + 50])
    X = np.array(vecs)
    np.savez(cache, X=X, texts=np.array(texts))
    return X


def main():
    rows = [json.loads(l) for l in (HERE / "dataset.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    X = load_embeddings(rows)
    baseline = json.loads((HERE / "baseline.json").read_text()) if (HERE / "baseline.json").exists() else {}
    (HERE / "models").mkdir(exist_ok=True)

    metrics = {}
    for f in FIELDS:
        y = [r[f] for r in rows]
        acc, f1, report = cv_report(X, y)
        metrics[f] = {"trained_cv_accuracy": acc, "trained_cv_macro_f1": f1}
        if f in baseline:
            metrics[f]["gemini_zero_shot_accuracy"] = baseline[f]
        print(f"\n== {f}: trained (5-fold CV) acc={acc:.1%} macro-F1={f1:.2f}", end="")
        print(f"  | Gemini zero-shot acc={baseline[f]:.1%}" if f in baseline else "  | run evaluate.py for the baseline")
        print(report)
        joblib.dump(LogisticRegression(max_iter=2000, class_weight="balanced").fit(X, y), HERE / "models" / f"{f}.joblib")

    (HERE / "metrics.json").write_text(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
