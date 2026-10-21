"""Post fake channel messages from the labeled set to a webhook.
Usage: python backend/simulator.py <webhook_url> [count=5]   (url "-" = print only)
"""
import json
import random
import sys
import urllib.request
from pathlib import Path

url = sys.argv[1]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
rows = [json.loads(l) for l in (Path(__file__).parent.parent / "data-pipeline" / "dataset.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]

for r in random.sample(rows, n):
    # ponytail: simplified payload, real Meta/Gmail payloads get mapped inside the webhook
    body = json.dumps({"channel": r["ch"], "from": f"+91{random.randint(7000000000, 9999999999)}", "text": r["text"]}).encode()
    if url == "-":
        print(body.decode(), "->", r["route"])
        continue
    req = urllib.request.Request(url, body, {"Content-Type": "application/json"})
    print(urllib.request.urlopen(req).status, r["text"])
