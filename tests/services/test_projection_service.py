from datetime import date
from decimal import Decimal

import pytest

from app.models import FixedRule, Source
from app.services import installments as inst_svc
from app.services import projection as svc
from app.services.seed import seed_all


@pytest.fixture
def seeded(db):
    seed_all(db)
    return db


def _principal(db):
    return db.query(Source).filter_by(slug="conta-principal").first()


def test_monthly_projection_aggregates_installments(seeded):
    src = _principal(seeded)
    inst_svc.create_plan(seeded, {
        "description": "iPhone", "installments_count": 12,
        "first_purchase_date": date(2026, 4, 3),
        "source_id": src.id, "category_id": 1,
        "input_mode": "total", "total_amount": Decimal("6240.00"),
    })
    rows = svc.project_months(seeded, start=date(2026, 5, 1), months=3)
    may = next(r for r in rows if r["year"] == 2026 and r["month"] == 5)
    assert may["installments_total"] == Decimal("520.00")


def test_monthly_projection_includes_fixed_rules(seeded):
    src = _principal(seeded)
    rule = FixedRule(
        description="Aluguel", expected_amount=Decimal("1800.00"),
        recurrence="monthly", day_of_month=5,
        source_id=src.id, category_id=1,
        payment_mode="debit", type="expense",
        active_from=date(2026, 1, 1),
    )
    seeded.add(rule)
    seeded.commit()
    rows = svc.project_months(seeded, start=date(2026, 5, 1), months=3)
    may = next(r for r in rows if r["month"] == 5)
    assert may["fixed_total"] == Decimal("1800.00")


def test_monthly_projection_computes_grand_total(seeded):
    src = _principal(seeded)
    inst_svc.create_plan(seeded, {
        "description": "Sofá", "installments_count": 3,
        "first_purchase_date": date(2026, 4, 3),
        "source_id": src.id, "category_id": 1,
        "input_mode": "total", "total_amount": Decimal("900.00"),
    })
    rule = FixedRule(
        description="Aluguel", expected_amount=Decimal("1800.00"),
        recurrence="monthly", day_of_month=5,
        source_id=src.id, category_id=1,
        payment_mode="debit", type="expense",
        active_from=date(2026, 1, 1),
    )
    seeded.add(rule)
    seeded.commit()
    rows = svc.project_months(seeded, start=date(2026, 5, 1), months=2)
    may = next(r for r in rows if r["month"] == 5)
    assert may["grand_total"] == Decimal("2100.00")


def test_ledger_for_month_lists_all_obligations_sorted(seeded):
    src = _principal(seeded)
    rule = FixedRule(
        description="Aluguel", expected_amount=Decimal("1800.00"),
        recurrence="monthly", day_of_month=5,
        source_id=src.id, category_id=1,
        payment_mode="debit", type="expense",
        active_from=date(2026, 1, 1),
    )
    seeded.add(rule)
    seeded.commit()
    inst_svc.create_plan(seeded, {
        "description": "iPhone", "installments_count": 12,
        "first_purchase_date": date(2026, 4, 3),
        "source_id": src.id, "category_id": 1,
        "input_mode": "total", "total_amount": Decimal("6240.00"),
    })
    rows = svc.ledger_for_month(seeded, year=2026, month=5)
    descs = [r["description"] for r in rows]
    assert any("Aluguel" in d for d in descs)
    assert any("iPhone" in d for d in descs)
    dates = [r["date"] for r in rows]
    assert dates == sorted(dates)
