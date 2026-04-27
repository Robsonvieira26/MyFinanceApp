from datetime import date
from decimal import Decimal

import pytest

from app.services import reports as svc
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


def test_monthly_totals_returns_last_n_months(seeded):
    tx_svc.create(seeded, _tx(date=date(2026, 2, 10), amount=Decimal("1000")))
    tx_svc.create(seeded, _tx(date=date(2026, 3, 10), amount=Decimal("2000")))
    tx_svc.create(seeded, _tx(date=date(2026, 4, 10), amount=Decimal("3000")))
    rows = svc.monthly_totals(seeded, up_to=date(2026, 4, 30), months=3)
    assert len(rows) == 3
    assert rows[0]["year"] == 2026 and rows[0]["month"] == 2
    assert rows[0]["total_expense"] == Decimal("1000.00")
    assert rows[2]["total_expense"] == Decimal("3000.00")


def test_monthly_totals_fills_missing_months_with_zero(seeded):
    tx_svc.create(seeded, _tx(date=date(2026, 4, 10), amount=Decimal("500")))
    rows = svc.monthly_totals(seeded, up_to=date(2026, 4, 30), months=3)
    totals = [r["total_expense"] for r in rows]
    assert totals == [Decimal("0.00"), Decimal("0.00"), Decimal("500.00")]


def test_category_breakdown_by_month(seeded):
    tx_svc.create(seeded, _tx(category_id=1, date=date(2026, 3, 10),
                               amount=Decimal("1800")))
    tx_svc.create(seeded, _tx(category_id=2, date=date(2026, 3, 10),
                               amount=Decimal("500")))
    tx_svc.create(seeded, _tx(category_id=1, date=date(2026, 4, 10),
                               amount=Decimal("1800")))
    rows = svc.category_breakdown_by_month(
        seeded, up_to=date(2026, 4, 30), months=2
    )
    march_moradia = rows["Moradia"][0]
    april_moradia = rows["Moradia"][1]
    assert march_moradia == Decimal("1800.00")
    assert april_moradia == Decimal("1800.00")
    assert rows["Mercado"][0] == Decimal("500.00")
    assert rows["Mercado"][1] == Decimal("0.00")


def test_month_labels_returns_yyyy_mm(seeded):
    labels = svc.month_labels(date(2026, 4, 30), months=3)
    assert labels == ["2026-02", "2026-03", "2026-04"]
