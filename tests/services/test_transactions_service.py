from datetime import date
from decimal import Decimal

import pytest

from app.services import transactions as svc
from app.services.seed import seed_all


@pytest.fixture
def seeded(db):
    seed_all(db)
    return db


def _tx_data(**overrides):
    base = {
        "description": "Mercado mensal",
        "amount": Decimal("123.45"),
        "date": date(2026, 4, 10),
        "source_id": 1,
        "category_id": 2,
        "payment_mode": "debit",
        "type": "expense",
        "note": None,
    }
    base.update(overrides)
    return base


def test_create_transaction_returns_persisted_row(seeded):
    tx = svc.create(seeded, _tx_data())
    assert tx.id is not None
    assert tx.description == "Mercado mensal"
    assert tx.amount == Decimal("123.45")
    assert tx.origin == "manual"
    assert tx.status == "confirmed"


def test_list_returns_empty_initially(seeded):
    assert svc.list_all(seeded) == []


def test_list_returns_in_descending_date(seeded):
    svc.create(seeded, _tx_data(date=date(2026, 4, 1), description="A"))
    svc.create(seeded, _tx_data(date=date(2026, 4, 10), description="B"))
    svc.create(seeded, _tx_data(date=date(2026, 4, 5), description="C"))
    results = svc.list_all(seeded)
    assert [t.description for t in results] == ["B", "C", "A"]


def test_filter_by_month(seeded):
    svc.create(seeded, _tx_data(date=date(2026, 3, 30), description="mar"))
    svc.create(seeded, _tx_data(date=date(2026, 4, 2), description="abr-1"))
    svc.create(seeded, _tx_data(date=date(2026, 4, 25), description="abr-2"))
    results = svc.list_all(seeded, year=2026, month=4)
    assert {t.description for t in results} == {"abr-1", "abr-2"}


def test_filter_by_source(seeded):
    svc.create(seeded, _tx_data(source_id=1, description="principal"))
    svc.create(seeded, _tx_data(source_id=2, description="va"))
    results = svc.list_all(seeded, source_id=2)
    assert [t.description for t in results] == ["va"]


def test_filter_by_category(seeded):
    svc.create(seeded, _tx_data(category_id=1, description="moradia"))
    svc.create(seeded, _tx_data(category_id=5, description="lazer"))
    results = svc.list_all(seeded, category_id=5)
    assert [t.description for t in results] == ["lazer"]


def test_filter_by_text_matches_description_icase(seeded):
    svc.create(seeded, _tx_data(description="Uber Centro"))
    svc.create(seeded, _tx_data(description="Padaria"))
    results = svc.list_all(seeded, text="uber")
    assert [t.description for t in results] == ["Uber Centro"]


def test_update_changes_fields(seeded):
    tx = svc.create(seeded, _tx_data(description="old"))
    updated = svc.update(seeded, tx.id, {"description": "new", "amount": Decimal("999.99")})
    assert updated.description == "new"
    assert updated.amount == Decimal("999.99")


def test_update_unknown_id_raises(seeded):
    with pytest.raises(LookupError):
        svc.update(seeded, 9999, {"description": "x"})


def test_delete_removes_row(seeded):
    tx = svc.create(seeded, _tx_data())
    svc.delete(seeded, tx.id)
    assert svc.list_all(seeded) == []


def test_delete_unknown_id_raises(seeded):
    with pytest.raises(LookupError):
        svc.delete(seeded, 9999)
