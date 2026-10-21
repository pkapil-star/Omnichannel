"""Offline check: classify() parses a Gemini response. Run: python backend/test_classifier.py"""
import json
from types import SimpleNamespace
from unittest import mock

import classifier

fake = SimpleNamespace(text=json.dumps({"intent": "faq", "sentiment": "neutral"}))
with mock.patch.object(classifier, "_call", return_value=fake):
    assert classifier.classify("when do you open?") == ("faq", "neutral")
print("ok")
