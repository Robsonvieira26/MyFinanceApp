from datetime import date
from decimal import Decimal

import pytest

from app.services import goals as svc


def test_create_goal(db):
    g = svc.create(db, {
        "title": "Viagem Chile", "target_amount": Decimal("10000.00"),
        "target_date": date(2026, 12, 31),
    })
    assert g.id is not None
    assert g.saved_amount == Decimal("0.00")
    assert g.active is True


def test_add_progress_increments_saved(db):
    g = svc.create(db, {"title": "x", "target_amount": Decimal("1000.00")})
    svc.add_progress(db, g.id, Decimal("200.00"))
    svc.add_progress(db, g.id, Decimal("300.00"))
    g = svc.get(db, g.id)
    assert g.saved_amount == Decimal("500.00")


def test_progress_percentage(db):
    g = svc.create(db, {"title": "x", "target_amount": Decimal("1000.00")})
    svc.add_progress(db, g.id, Decimal("250.00"))
    assert svc.progress_pct(svc.get(db, g.id)) == 25.0


def test_archive_goal(db):
    g = svc.create(db, {"title": "x", "target_amount": Decimal("100")})
    svc.archive(db, g.id)
    assert svc.get(db, g.id).active is False


def test_list_excludes_archived_by_default(db):
    a = svc.create(db, {"title": "ativa", "target_amount": Decimal("100")})
    b = svc.create(db, {"title": "inativa", "target_amount": Decimal("100")})
    svc.archive(db, b.id)
    active = svc.list_all(db)
    assert [g.id for g in active] == [a.id]


def test_get_unknown_raises(db):
    with pytest.raises(LookupError):
        svc.get(db, 999)
