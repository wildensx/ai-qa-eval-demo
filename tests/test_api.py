"""API contract tests: status codes, schema, validation, auth and pagination."""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
KEY = {"X-API-Key": "demo-key"}


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_ask_returns_documented_schema():
    body = client.post("/ask", json={"question": "When does online check-in open?"}, headers=KEY).json()
    assert set(body) == {"answer", "citations", "abstained", "flags"}
    assert isinstance(body["citations"], list) and isinstance(body["abstained"], bool)


@pytest.mark.parametrize("headers", [{}, {"X-API-Key": "wrong"}])
def test_ask_rejects_missing_or_wrong_key(headers):
    response = client.post("/ask", json={"question": "When does online check-in open?"}, headers=headers)
    assert response.status_code == 401
    assert "answer" not in response.json()


@pytest.mark.parametrize("payload", [{}, {"question": ""}, {"question": "hi"}, {"question": "x" * 501}, {"question": 42}])
def test_ask_validates_input(payload):
    assert client.post("/ask", json=payload, headers=KEY).status_code == 422


def test_ask_is_deterministic_for_repeated_requests():
    question = {"question": "How many miles are required for Gold status?"}
    first, second = (client.post("/ask", json=question, headers=KEY).json() for _ in range(2))
    assert first == second


def test_documents_pagination_covers_every_item_once():
    total = client.get("/documents").json()["total"]
    seen = []
    for offset in range(0, total, 2):
        page = client.get("/documents", params={"limit": 2, "offset": offset}).json()
        assert len(page["items"]) <= 2
        seen += [item["id"] for item in page["items"]]
    assert len(seen) == total and len(set(seen)) == total


def test_documents_offset_past_end_returns_empty_page():
    page = client.get("/documents", params={"offset": 999}).json()
    assert page["items"] == [] and page["total"] > 0


@pytest.mark.parametrize("params", [{"limit": 0}, {"limit": 51}, {"offset": -1}])
def test_documents_rejects_out_of_range_paging(params):
    assert client.get("/documents", params=params).status_code == 422


def test_unknown_document_returns_404():
    response = client.get("/documents/does-not-exist")
    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}
