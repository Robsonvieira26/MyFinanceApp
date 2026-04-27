from datetime import date
from decimal import Decimal

from app.models import Source, Transaction


def _make_source(db, **overrides):
    base = {"slug": "x", "name": "X", "kind": "hybrid", "closing_day": 4, "due_day": 10}
    base.update(overrides)
    s = Source(**base)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def test_debit_transaction_due_date_equals_transaction_date(db):
    src = _make_source(db)
    tx = Transaction(
        description="x", amount=Decimal("10"), date=date(2026, 4, 15),
        source_id=src.id, category_id=1, payment_mode="debit",
    )
    assert tx.compute_due_date(src) == date(2026, 4, 15)


def test_pix_transaction_due_date_equals_transaction_date(db):
    src = _make_source(db)
    tx = Transaction(
        description="x", amount=Decimal("10"), date=date(2026, 4, 15),
        source_id=src.id, category_id=1, payment_mode="pix",
    )
    assert tx.compute_due_date(src) == date(2026, 4, 15)


def test_credit_before_closing_goes_to_same_month_invoice(db):
    src = _make_source(db, closing_day=4, due_day=10)
    tx = Transaction(
        description="x", amount=Decimal("10"), date=date(2026, 4, 3),
        source_id=src.id, category_id=1, payment_mode="credit",
    )
    assert tx.compute_due_date(src) == date(2026, 4, 10)


def test_credit_after_closing_goes_to_next_month_invoice(db):
    src = _make_source(db, closing_day=4, due_day=10)
    tx = Transaction(
        description="x", amount=Decimal("10"), date=date(2026, 4, 5),
        source_id=src.id, category_id=1, payment_mode="credit",
    )
    assert tx.compute_due_date(src) == date(2026, 5, 10)


def test_credit_without_source_cycle_falls_back_to_date(db):
    src = _make_source(db, closing_day=None, due_day=None, kind="debit")
    tx = Transaction(
        description="x", amount=Decimal("10"), date=date(2026, 4, 5),
        source_id=src.id, category_id=1, payment_mode="credit",
    )
    assert tx.compute_due_date(src) == date(2026, 4, 5)
