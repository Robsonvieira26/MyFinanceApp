from datetime import date
from decimal import Decimal

import pytest

from app.models import Source, Transaction
from app.services import installments as svc
from app.services.seed import seed_all


@pytest.fixture
def seeded(db):
    seed_all(db)
    return db


def _principal(db):
    return db.query(Source).filter_by(slug="conta-principal").first()


def test_create_from_total_splits_evenly(seeded):
    plan = svc.create_plan(seeded, {
        "description": "iPhone 14",
        "installments_count": 12,
        "first_purchase_date": date(2026, 4, 3),
        "source_id": _principal(seeded).id,
        "category_id": 1,
        "input_mode": "total",
        "total_amount": Decimal("6240.00"),
    })
    assert plan.id is not None
    assert plan.total_amount == Decimal("6240.00")
    assert plan.installment_amount == Decimal("520.00")


def test_create_from_per_installment_multiplies(seeded):
    plan = svc.create_plan(seeded, {
        "description": "Sofá",
        "installments_count": 6,
        "first_purchase_date": date(2026, 4, 15),
        "source_id": _principal(seeded).id,
        "category_id": 1,
        "input_mode": "per_installment",
        "installment_amount": Decimal("350.00"),
    })
    assert plan.total_amount == Decimal("2100.00")
    assert plan.installment_amount == Decimal("350.00")


def test_create_plan_generates_N_transactions(seeded):
    plan = svc.create_plan(seeded, {
        "description": "iPhone",
        "installments_count": 12,
        "first_purchase_date": date(2026, 4, 3),
        "source_id": _principal(seeded).id,
        "category_id": 1,
        "input_mode": "total",
        "total_amount": Decimal("6240.00"),
    })
    txs = seeded.query(Transaction).filter_by(origin="installment",
                                                origin_ref_id=plan.id).all()
    assert len(txs) == 12
    assert all(tx.amount == Decimal("520.00") for tx in txs)
    assert all(tx.payment_mode == "credit" for tx in txs)
    assert all(tx.origin == "installment" for tx in txs)


def test_first_installment_respects_closing_before(seeded):
    plan = svc.create_plan(seeded, {
        "description": "a",
        "installments_count": 3,
        "first_purchase_date": date(2026, 4, 3),
        "source_id": _principal(seeded).id,
        "category_id": 1,
        "input_mode": "total",
        "total_amount": Decimal("300.00"),
    })
    txs = sorted(
        seeded.query(Transaction).filter_by(origin="installment",
                                              origin_ref_id=plan.id).all(),
        key=lambda t: t.date,
    )
    assert txs[0].date == date(2026, 4, 10)
    assert txs[1].date == date(2026, 5, 10)
    assert txs[2].date == date(2026, 6, 10)


def test_first_installment_respects_closing_after(seeded):
    plan = svc.create_plan(seeded, {
        "description": "b",
        "installments_count": 3,
        "first_purchase_date": date(2026, 4, 5),
        "source_id": _principal(seeded).id,
        "category_id": 1,
        "input_mode": "total",
        "total_amount": Decimal("300.00"),
    })
    txs = sorted(
        seeded.query(Transaction).filter_by(origin="installment",
                                              origin_ref_id=plan.id).all(),
        key=lambda t: t.date,
    )
    assert txs[0].date == date(2026, 5, 10)
    assert txs[1].date == date(2026, 6, 10)
    assert txs[2].date == date(2026, 7, 10)


def test_installments_are_projected_until_real_date(seeded):
    plan = svc.create_plan(seeded, {
        "description": "c",
        "installments_count": 3,
        "first_purchase_date": date(2026, 4, 3),
        "source_id": _principal(seeded).id,
        "category_id": 1,
        "input_mode": "total",
        "total_amount": Decimal("300.00"),
    })
    txs = seeded.query(Transaction).filter_by(origin_ref_id=plan.id).all()
    assert all(tx.status == "projected" for tx in txs)


def test_create_on_non_credit_source_raises(seeded):
    va = seeded.query(Source).filter_by(slug="va").first()
    with pytest.raises(ValueError, match="só em fontes com crédito"):
        svc.create_plan(seeded, {
            "description": "x",
            "installments_count": 3,
            "first_purchase_date": date(2026, 4, 1),
            "source_id": va.id,
            "category_id": 1,
            "input_mode": "total",
            "total_amount": Decimal("300.00"),
        })


def test_delete_plan_removes_unconfirmed_transactions(seeded):
    plan = svc.create_plan(seeded, {
        "description": "del",
        "installments_count": 3,
        "first_purchase_date": date(2026, 4, 3),
        "source_id": _principal(seeded).id,
        "category_id": 1,
        "input_mode": "total",
        "total_amount": Decimal("300.00"),
    })
    svc.delete_plan(seeded, plan.id)
    remaining = seeded.query(Transaction).filter_by(origin_ref_id=plan.id).all()
    assert remaining == []


def test_delete_plan_keeps_already_confirmed(seeded):
    plan = svc.create_plan(seeded, {
        "description": "del2",
        "installments_count": 3,
        "first_purchase_date": date(2026, 4, 3),
        "source_id": _principal(seeded).id,
        "category_id": 1,
        "input_mode": "total",
        "total_amount": Decimal("300.00"),
    })
    first_tx = seeded.query(Transaction).filter_by(origin_ref_id=plan.id).order_by(
        Transaction.date
    ).first()
    first_tx.status = "confirmed"
    seeded.commit()

    svc.delete_plan(seeded, plan.id)

    remaining = seeded.query(Transaction).filter_by(origin_ref_id=plan.id).all()
    assert len(remaining) == 1
    assert remaining[0].status == "confirmed"
