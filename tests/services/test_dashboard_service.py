from datetime import date
from decimal import Decimal

import pytest

from app.services import dashboard as svc
from app.services import transactions as tx_svc
from app.services.seed import seed_all


@pytest.fixture
def seeded(db):
    seed_all(db)
    return db


def _tx(**over):
    base = {
        "description": "x", "amount": Decimal("100"),
        "date": date(2026, 4, 15), "source_id": 1, "category_id": 2,
        "payment_mode": "debit", "type": "expense",
    }
    base.update(over)
    return base


def test_month_totals_sums_expenses_of_the_month(seeded):
    tx_svc.create(seeded, _tx(amount=Decimal("100"), date=date(2026, 4, 1)))
    tx_svc.create(seeded, _tx(amount=Decimal("250"), date=date(2026, 4, 20)))
    tx_svc.create(seeded, _tx(amount=Decimal("80"), date=date(2026, 3, 31)))
    out = svc.month_overview(seeded, year=2026, month=4)
    assert out["total_expense"] == Decimal("350.00")


def test_month_totals_separates_income(seeded):
    tx_svc.create(seeded, _tx(type="expense", amount=Decimal("300")))
    tx_svc.create(seeded, _tx(type="income", amount=Decimal("8500"),
                              payment_mode="pix", date=date(2026, 4, 5)))
    out = svc.month_overview(seeded, year=2026, month=4)
    assert out["total_expense"] == Decimal("300.00")
    assert out["total_income"] == Decimal("8500.00")


def test_top_categories_returns_sorted_limited(seeded):
    tx_svc.create(seeded, _tx(category_id=1, amount=Decimal("1800")))
    tx_svc.create(seeded, _tx(category_id=2, amount=Decimal("890")))
    tx_svc.create(seeded, _tx(category_id=3, amount=Decimal("410")))
    tx_svc.create(seeded, _tx(category_id=5, amount=Decimal("320")))
    tx_svc.create(seeded, _tx(category_id=9, amount=Decimal("50")))
    out = svc.top_categories(seeded, year=2026, month=4, limit=4)
    names = [r["name"] for r in out]
    assert names == ["Moradia", "Mercado", "Transporte", "Lazer"]
    assert out[0]["total"] == Decimal("1800.00")


def test_by_source_distribution(seeded):
    tx_svc.create(seeded, _tx(source_id=1, amount=Decimal("1000")))
    tx_svc.create(seeded, _tx(source_id=2, amount=Decimal("200")))
    tx_svc.create(seeded, _tx(source_id=3, amount=Decimal("0.01")))
    out = svc.by_source(seeded, year=2026, month=4)
    totals = {r["slug"]: r["total"] for r in out}
    assert totals["conta-principal"] == Decimal("1000.00")
    assert totals["va"] == Decimal("200.00")


def test_month_overview_includes_counts(seeded):
    tx_svc.create(seeded, _tx(amount=Decimal("10")))
    tx_svc.create(seeded, _tx(amount=Decimal("20")))
    out = svc.month_overview(seeded, year=2026, month=4)
    assert out["count"] == 2
