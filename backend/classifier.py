"""classify(text) -> (intent, sentiment) via Gemini on Vertex AI. Only Gemini call site: _call()."""
import functools
import json
import os
from pathlib import Path

from google import genai
from google.genai import types

_env = Path(__file__).parent.parent / ".env"
if _env.exists():
    for line in _env.read_text(encoding="utf-8").splitlines():
        k, _, v = line.partition("=")
        if v.strip() and not k.startswith("#"):
            os.environ.setdefault(k.strip(), v.strip())

MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash")
PROMPT = """Classify this customer message sent to a small local business.
intent: faq (general question about hours, location, prices, services, policies), booking (wants to book, change or cancel an appointment), complaint (unhappy about something that already happened), other (anything else).
sentiment: positive, neutral or negative (tone of the customer).
Message: """
SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "intent": {"type": "STRING", "enum": ["faq", "booking", "complaint", "other"]},
        "sentiment": {"type": "STRING", "enum": ["positive", "neutral", "negative"]},
    },
    "required": ["intent", "sentiment"],
}


@functools.cache
def _client():
    return genai.Client(
        vertexai=True,
        project=os.environ["GCP_PROJECT_ID"],
        location=os.environ.get("GCP_LOCATION", "us-central1"),
        http_options=types.HttpOptions(retry_options=types.HttpRetryOptions(attempts=5)),
    )


def _call(text):
    return _client().models.generate_content(
        model=MODEL,
        contents=PROMPT + text,
        config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=SCHEMA, temperature=0),
    )


EMBED_MODEL = os.environ.get("GEMINI_EMBED_MODEL", "gemini-embedding-001")


def embed(texts):
    """List of strings -> list of vectors. Used for training features."""
    r = _client().models.embed_content(model=EMBED_MODEL, contents=texts)
    return [e.values for e in r.embeddings]


def classify(text):
    r = json.loads(_call(text).text)
    return r["intent"], r["sentiment"]
