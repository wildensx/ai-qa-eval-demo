"""End-to-end check of the demo UI with Playwright (pytest-playwright)."""
import socket
import threading
import time

import pytest
import uvicorn

from app.main import app

pytest.importorskip("pytest_playwright")
from playwright.sync_api import expect  # noqa: E402


@pytest.fixture(scope="session")
def base_url():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    while not server.started:
        time.sleep(0.05)
    yield f"http://127.0.0.1:{port}"
    server.should_exit = True
    thread.join(timeout=5)


def ask(page, base_url, question):
    page.goto(base_url)
    page.get_by_label("Ask about refunds").fill(question)
    page.get_by_role("button", name="Ask").click()


def test_user_gets_grounded_answer_with_source(page, base_url):
    ask(page, base_url, "How many days do I have to request a full refund?")
    expect(page.get_by_test_id("answer")).to_contain_text("14 days")
    expect(page.get_by_test_id("citations")).to_have_text("Source: refunds")


def test_out_of_scope_question_is_declined(page, base_url):
    ask(page, base_url, "Do you fly to Mars?")
    expect(page.get_by_test_id("answer")).to_have_text("I can't find that in the available documents.")
    expect(page.get_by_test_id("citations")).to_be_empty()
