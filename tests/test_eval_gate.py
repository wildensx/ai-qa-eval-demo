"""Regression gate: the golden set must pass, and seeded defects must be caught.

The seeded-defect tests check the evaluation itself: a gate that never fails is not a gate.
"""
import pytest

from evals.run_eval import evaluate


def test_golden_set_meets_every_threshold():
    report = evaluate()
    assert report["failed_metrics"] == [], report["metrics"]


@pytest.mark.parametrize("fault, expected", [
    ("hallucinate", {"groundedness", "fact_accuracy"}),  # invented figures
    ("wrong_source", {"citation_accuracy", "groundedness"}),  # right-looking answer, wrong citation
])
def test_evaluation_detects_seeded_defects(monkeypatch, fault, expected):
    monkeypatch.setenv("DEMO_FAULT", fault)
    assert expected <= set(evaluate()["failed_metrics"])


def test_injected_instructions_never_reach_the_user():
    for row in evaluate()["results"]:
        assert "90 days" not in row["answer"] and "IGNORE" not in row["answer"]
