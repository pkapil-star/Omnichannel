"""Unit test for the training critical path, no API calls. Run: python data-pipeline/test_train.py"""
import numpy as np

from train import cv_report

rng = np.random.default_rng(0)
labels = np.repeat(["a", "b", "c"], 20)
centers = {"a": 0.0, "b": 5.0, "c": -5.0}
X = np.array([rng.normal(centers[l], 1.0, 16) for l in labels])

acc, f1, _ = cv_report(X, list(labels))
assert acc > 0.9 and f1 > 0.9, (acc, f1)
print(f"ok: cv accuracy {acc:.2f} on separable synthetic data")
