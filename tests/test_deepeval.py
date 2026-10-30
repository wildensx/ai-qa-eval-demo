"""DeepEval: a deterministic custom metric that runs offline, plus an LLM-judged GEval that runs when an API key is set."""
import os
import re

import pytest
from deepeval import assert_test
from deepeval.metrics import BaseMetric, GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams
from fastapi.testclient import TestClient

from app.documents import DOCUMENTS
from app.main import app
from evals.run_eval import load_cases

SOURCES = {d["id"]: d["text"] for d in DOCUMENTS}
client = TestClient(app)


class SourceGroundedness(BaseMetric):
    """Share of numbers in the answer that also appear in the retrieved source. Catches invented figures."""

    def __init__(self, threshold=1.0):
        self.threshold = threshold

    def measure(self, test_case, *args, **kwargs):
        numbers = re.findall(r"\d+", test_case.actual_output)
        context = re.findall(r"\d+", " ".join(test_case.retrieval_context or []))
        found = [n for n in numbers if n in context]
        self.score = len(found) / len(numbers) if numbers else 1.0
        self.success = self.score >= self.threshold
        self.reason = f"{len(found)}/{len(numbers)} numbers found in the cited source"
        return self.score

    async def a_measure(self, test_case, *args, **kwargs):
        return self.measure(test_case)

    def is_successful(self):
        return self.success

    @property
    def __name__(self):
        return "Source groundedness"


def to_test_case(case):
    body = client.post("/ask", json={"question": case["question"]}, headers={"X-API-Key": "demo-key"}).json()
    return LLMTestCase(input=case["question"], actual_output=body["answer"],
                       retrieval_context=[SOURCES[c] for c in body["citations"]])


ANSWERABLE = [c for c in load_cases() if c["type"] == "answerable"]


@pytest.mark.parametrize("case", ANSWERABLE, ids=[c["id"] for c in ANSWERABLE])
def test_answers_are_grounded_in_their_source(case):
    assert_test(to_test_case(case), [SourceGroundedness()], run_async=False)


def test_metric_flags_an_invented_number():
    metric = SourceGroundedness()
    case = LLMTestCase(input="Refund window?", actual_output="You can get a full refund within 30 days.",
                       retrieval_context=[SOURCES["refunds"]])
    metric.measure(case)
    assert not metric.is_successful() and metric.reason == "0/1 numbers found in the cited source"


@pytest.mark.skipif(not os.environ.get("OPENAI_API_KEY"), reason="LLM-judged metric: set OPENAI_API_KEY to run")
def test_answer_correctness_with_geval():
    correctness = GEval(name="Correctness", threshold=0.7,
                        criteria="Is the actual output factually consistent with the retrieval context and does it answer the input?",
                        evaluation_params=[SingleTurnParams.INPUT, SingleTurnParams.ACTUAL_OUTPUT, SingleTurnParams.RETRIEVAL_CONTEXT])
    assert_test(to_test_case(ANSWERABLE[0]), [correctness], run_async=False)
