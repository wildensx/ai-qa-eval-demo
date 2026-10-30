"""Data validation with plain SQL: each named check in sql/checks.sql must find exactly the planted problems."""
import re
import sqlite3
from pathlib import Path

import pytest

SQL = Path(__file__).resolve().parent.parent / "sql"


def load_checks():
    text = (SQL / "checks.sql").read_text(encoding="utf-8")
    return {m.group(1): m.group(2).strip() for m in re.finditer(r"-- name: (\w+)\n(.*?)(?=\n-- name:|\Z)", text, re.S)}


@pytest.fixture(scope="module")
def db():
    conn = sqlite3.connect(":memory:")
    conn.executescript((SQL / "schema_and_seed.sql").read_text(encoding="utf-8"))
    yield conn
    conn.close()


CHECKS = load_checks()


@pytest.mark.parametrize("name, expected", [
    ("duplicate_customer_emails", [("ana@example.com", 2)]),
    ("orphan_bookings", [(12,)]),
    ("refunds_exceeding_booking", [(102, 250, 200)]),
    ("full_refunds_outside_policy_window", [(101, 28.0)]),
])
def test_check_finds_planted_problem(db, name, expected):
    assert db.execute(CHECKS[name]).fetchall() == expected


def test_every_refund_reconciles_to_a_booking(db):
    refunds_total, matched_total = db.execute(CHECKS["refund_total_reconciliation"]).fetchone()
    assert refunds_total == matched_total
