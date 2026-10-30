# AI QA evaluation demo

[![tests](https://github.com/wildensx/ai-qa-eval-demo/actions/workflows/ci.yml/badge.svg)](https://github.com/wildensx/ai-qa-eval-demo/actions/workflows/ci.yml)

A small, self-contained example of how I test an AI assistant, using the tools I work with: Playwright (Python and TypeScript), pytest, DeepEval, promptfoo and SQL, all running in GitHub Actions.

The system under test is a toy "policy assistant" for a fictional travel company. It retrieves a document and answers with a sentence from it. It has no LLM inside, so everything runs offline and gives the same result every time. **All data is synthetic.**

## Demos

| Tool | Where | What it shows |
|---|---|---|
| Golden-set evaluation (Python) | [`evals/`](evals/) | 20 cases: correct source cited, facts present, numbers grounded in the source, out-of-scope questions declined, prompt injection flagged and never echoed |
| pytest | [`tests/test_eval_gate.py`](tests/test_eval_gate.py) | The evaluation as a CI gate, plus seeded defects (invented numbers, wrong citation) that must make it fail |
| API testing (pytest + httpx) | [`tests/test_api.py`](tests/test_api.py) | Schema, 401 on bad key, 422 on invalid input, repeatable answers, pagination with no gaps or duplicates, 404 contract |
| DeepEval | [`tests/test_deepeval.py`](tests/test_deepeval.py) | A custom offline metric (source groundedness) on every answer; an LLM-judged GEval that runs when an API key is present |
| promptfoo + JavaScript | [`promptfoo/`](promptfoo/) | HTTP target with JavaScript assertions: expected facts, abstention, injection resistance, no invented numbers |
| Playwright (TypeScript) | [`ts-e2e/`](ts-e2e/) | UI flows and API checks with the `request` fixture; the service starts from the Playwright config |
| Playwright (Python) | [`tests/e2e/`](tests/e2e/) | The same UI flows with pytest-playwright |
| SQL | [`sql/`](sql/) | Data checks for duplicates, orphan records, refunds larger than the booking, policy-window breaches and total reconciliation |

## What the evaluation caught

The first run of the golden set failed on four cases, and each failure pointed at a real defect in the assistant: a refund question answered with the wrong sentence, a check-in question answered from the baggage policy, an out-of-scope question answered instead of declined, and an injected question that pulled in a malicious partner document. Fixes: plural normalisation, and untrusted instructions removed from the index, not only from the reply.

## Run it

```bash
python -m venv .venv && .venv/Scripts/activate      # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt && python -m playwright install chromium
python -m pytest -v                                 # API, eval gate, DeepEval, SQL, Playwright Python
python -m evals.run_eval                            # writes reports/eval_report.md
cd ts-e2e && npm install && npx playwright test     # Playwright TypeScript
uvicorn app.main:app --port 8765                    # then, in promptfoo/: npx promptfoo@0.125.1 eval
```

## How it was built

I designed the test strategy, the golden set, the checks and the seeded defects. The code was implemented with AI coding assistants, and I reviewed it and validated the behaviour.

Wilde Valdez · Senior QA Engineer · [LinkedIn](https://www.linkedin.com/in/wilde-valdez)
