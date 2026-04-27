from datetime import date
from decimal import Decimal

import pytest

from app.services import alerts as svc
from app.services import budgets as bud_svc
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


def test_no_alerts_when_under_80pct(seeded):
    bud_svc.set_category(seeded, category_id=5, amount=Decimal("400"))
    tx_svc.create(seeded, _tx(category_id=5, amount=Decimal("200")))  # 50%
    out = svc.evaluate(seeded, year=2026, month=4)
    assert out == []


def test_alert_when_category_reaches_80pct(seeded):
    bud_svc.set_category(seeded, category_id=5, amount=Decimal("400"))
    tx_svc.create(seeded, _tx(category_id=5, amount=Decimal("320")))  # 80%
    out = svc.evaluate(seeded, year=2026, month=4)
    assert len(out) == 1
    assert out[0]["level"] == "warn"
    assert "Lazer" in out[0]["message"]
    assert out[0]["kind"] == "category_threshold"


def test_alert_when_total_reaches_90pct(seeded):
    bud_svc.set_total(seeded, Decimal("1000"))
    tx_svc.create(seeded, _tx(amount=Decimal("900")))  # 90%
    out = svc.evaluate(seeded, year=2026, month=4)
    kinds = [a["kind"] for a in out]
    assert "total_threshold" in kinds


def test_no_alert_when_no_budget_set(seeded):
    tx_svc.create(seeded, _tx(amount=Decimal("99999")))
    out = svc.evaluate(seeded, year=2026, month=4)
    assert out == []


def test_alert_level_err_above_100pct(seeded):
    bud_svc.set_category(seeded, category_id=5, amount=Decimal("400"))
    tx_svc.create(seeded, _tx(category_id=5, amount=Decimal("450")))  # 112%
    out = svc.evaluate(seeded, year=2026, month=4)
    assert out[0]["level"] == "err"
