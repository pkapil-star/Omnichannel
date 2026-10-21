"""Sanity check for the labeled set. Run: python data-pipeline/test_dataset.py"""
import json
from pathlib import Path

here = Path(__file__).parent
faq_ids = {f["id"] for f in json.loads((here / "faqs.json").read_text(encoding="utf-8"))["faqs"]}
rows = [json.loads(l) for l in (here / "dataset.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]

assert len(rows) >= 100, len(rows)
assert len({r["text"] for r in rows}) == len(rows), "duplicate text"
for r in rows:
    assert r["ch"] in {"whatsapp", "instagram", "gmail"}, r
    assert r["intent"] in {"faq", "booking", "complaint", "other"}, r
    assert r["sent"] in {"positive", "neutral", "negative"}, r
    assert r["faq"] is None or r["faq"] in faq_ids, r
    # route must follow the 3-condition gate: negative -> push; faq+match -> auto_reply; else queue
    want = "push" if r["sent"] == "negative" else "auto_reply" if r["intent"] == "faq" and r["faq"] else "queue"
    assert r["route"] == want, r

assert {r["faq"] for r in rows if r["route"] == "auto_reply"} == faq_ids, "every FAQ needs >=1 example"
print(f"ok: {len(rows)} rows", {k: sum(r["route"] == k for r in rows) for k in ("auto_reply", "push", "queue")})
