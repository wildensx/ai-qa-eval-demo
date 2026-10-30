"""A deliberately small retrieval + extractive answer service.

It has no LLM inside, so the test suite runs offline and deterministically.
The point of the project is the testing around it, not the assistant itself.
"""
import os
import re
from collections import Counter
from math import log

from .documents import DOCUMENTS

STOPWORDS = set("a an the of to in on for and or is are can do does how what when my i be with by at as it if".split())
INJECTION = re.compile(r"ignore (all )?(previous|prior) instructions|disregard (the )?(rules|instructions)|system prompt", re.I)
MIN_SCORE = 1.5
NO_ANSWER = "I can't find that in the available documents."


def tokens(text):
    words = [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOPWORDS]
    return [w[:-1] if len(w) > 3 and w.endswith("s") else w for w in words]  # refunds -> refund, opens -> open


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=\.)\s+", text) if s.strip()]


def trusted_text(doc):
    """Untrusted instructions inside a document are neither indexed nor repeated to the user."""
    return " ".join(s for s in sentences(doc["text"]) if not INJECTION.search(s))


_DF = Counter(t for doc in DOCUMENTS for t in set(tokens(trusted_text(doc) + " " + doc["title"])))


def _idf(term):
    return log((len(DOCUMENTS) + 1) / (_DF.get(term, 0) + 0.5))


def retrieve(question, k=2):
    q = set(tokens(question))
    scored = []
    for doc in DOCUMENTS:
        words = set(tokens(trusted_text(doc) + " " + doc["title"]))
        scored.append((sum(_idf(t) for t in q & words), doc))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [(round(score, 3), doc) for score, doc in scored[:k] if score > 0]


def answer(question):
    """Returns the answer, the cited document ids and safety flags."""
    flags = ["prompt_injection_in_question"] if INJECTION.search(question) else []
    hits = retrieve(question)
    if not hits or hits[0][0] < MIN_SCORE:
        return dict(answer=NO_ANSWER, citations=[], abstained=True, flags=flags)
    score, doc = hits[0]
    q = set(tokens(question))
    safe = sentences(trusted_text(doc))
    if trusted_text(doc) != doc["text"]:
        flags.append("prompt_injection_in_source")
    best = max(safe, key=lambda s: len(q & set(tokens(s)))) if safe else NO_ANSWER
    text = best
    fault = os.environ.get("DEMO_FAULT", "")
    if fault == "hallucinate":  # seeded defect used to prove the evaluation catches it
        text = re.sub(r"\d+", lambda m: str(int(m.group()) * 2), best)
    if fault == "wrong_source":
        doc = hits[-1][1]
    return dict(answer=text, citations=[doc["id"]], abstained=False, flags=flags)
