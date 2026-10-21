"""Score the classifier on the labeled set.
Usage: python data-pipeline/evaluate.py [limit] [delay_seconds=4]   (4s keeps under free-tier 15 req/min)
"""
import json
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
from classifier import classify

rows = [json.loads(l) for l in (Path(__file__).parent / "dataset.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
rows = rows[: int(sys.argv[1])] if len(sys.argv) > 1 else rows
delay = float(sys.argv[2]) if len(sys.argv) > 2 else 4

hit = Counter()
confusion = {"intent": Counter(), "sent": Counter()}
for r in rows:
    intent, sent = classify(r["text"])
    for field, got in (("intent", intent), ("sent", sent)):
        confusion[field][(r[field], got)] += 1
        hit[field] += got == r[field]
    time.sleep(delay)

for field in ("intent", "sent"):
    print(f"\n{field}: {hit[field]}/{len(rows)} = {hit[field] / len(rows):.1%}")
    print("  true -> predicted : count")
    for (want, got), n in sorted(confusion[field].items()):
        print(f"  {want:>10} -> {got:<10}: {n}{'' if want == got else '  <-- miss'}")
