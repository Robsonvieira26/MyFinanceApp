from decimal import Decimal

import pytest

from app.services import budgets as svc
from app.services.seed import seed_all


@pytest.fixture
def seeded(db):
    seed_all(db)
    return db


def test_set_total_budget_creates_row(seeded):
    b = svc.set_total(seeded, Decimal("5000.00"))
    assert b.scope == "total"
    assert b.amount == Decimal("5000.00")
    assert b.category_id is None


def test_set_total_budget_updates_existing(seeded):
    svc.set_total(seeded, Decimal("5000.00"))
    b = svc.set_total(seeded, Decimal("6000.00"))
    assert b.amount == Decimal("6000.00")
    assert len(svc.list_all(seeded)) == 1


def test_set_category_budget(seeded):
    b = svc.set_category(seeded, category_id=5, amount=Decimal("400.00"))
    assert b.scope == "category"
    assert b.category_id == 5
    assert b.amount == Decimal("400.00")


def test_get_total_returns_none_if_not_set(seeded):
    assert svc.get_total(seeded) is None


def test_get_total_returns_amount(seeded):
    svc.set_total(seeded, Decimal("5000.00"))
    assert svc.get_total(seeded) == Decimal("5000.00")


def test_get_category_returns_dict(seeded):
    svc.set_category(seeded, category_id=1, amount=Decimal("1800.00"))
    svc.set_category(seeded, category_id=5, amount=Decimal("400.00"))
    result = svc.get_by_category(seeded)
    assert result[1] == Decimal("1800.00")
    assert result[5] == Decimal("400.00")
