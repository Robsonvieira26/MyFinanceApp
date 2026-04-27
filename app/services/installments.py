from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from sqlalchemy.orm import Session

from app.models import InstallmentPlan, Source, Transaction
from app.services.fatura import fatura_due_month


def _quantize(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _next_due_date(base_due: date, months_ahead: int) -> date:
    month_index = base_due.month - 1 + months_ahead
    year = base_due.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, base_due.day)


def create_plan(db: Session, data: dict[str, Any]) -> InstallmentPlan:
    source = db.get(Source, data["source_id"])
    if source is None:
        raise LookupError(f"Source {data['source_id']} not found")
    if source.closing_day is None or source.due_day is None:
        raise ValueError(
            "Parcelamentos só em fontes com crédito (closing_day + due_day)"
        )

    count = int(data["installments_count"])
    mode = data["input_mode"]
    if mode == "total":
        total = Decimal(data["total_amount"])
        per = _quantize(total / Decimal(count))
    elif mode == "per_installment":
        per = Decimal(data["installment_amount"])
        total = _quantize(per * Decimal(count))
    else:
        raise ValueError(f"input_mode inválido: {mode}")

    plan = InstallmentPlan(
        description=data["description"],
        total_amount=_quantize(total),
        installments_count=count,
        installment_amount=per,
        first_purchase_date=data["first_purchase_date"],
        source_id=source.id,
        category_id=data["category_id"],
        active=True,
    )
    db.add(plan)
    db.flush()

    first_due = fatura_due_month(
        plan.first_purchase_date, source.closing_day, source.due_day
    )
    for i in range(count):
        due = _next_due_date(first_due, i)
        tx = Transaction(
            description=f"{plan.description} — parcela {i + 1}/{count}",
            amount=per,
            date=due,
            source_id=source.id,
            category_id=plan.category_id,
            payment_mode="credit",
            type="expense",
            origin="installment",
            origin_ref_id=plan.id,
            status="projected",
        )
        db.add(tx)

    db.commit()
    db.refresh(plan)
    return plan


def list_plans(db: Session, *, active_only: bool = True) -> list[InstallmentPlan]:
    q = db.query(InstallmentPlan)
    if active_only:
        q = q.filter(InstallmentPlan.active.is_(True))
    return q.order_by(InstallmentPlan.first_purchase_date.desc()).all()


def get_plan(db: Session, plan_id: int) -> InstallmentPlan:
    plan = db.get(InstallmentPlan, plan_id)
    if plan is None:
        raise LookupError(f"InstallmentPlan {plan_id} not found")
    return plan


def delete_plan(db: Session, plan_id: int) -> None:
    plan = get_plan(db, plan_id)
    db.query(Transaction).filter(
        Transaction.origin_ref_id == plan.id,
        Transaction.origin == "installment",
        Transaction.status == "projected",
    ).delete(synchronize_session=False)
    db.delete(plan)
    db.commit()


def confirm_installment(db: Session, tx_id: int) -> Transaction:
    tx = db.get(Transaction, tx_id)
    if tx is None or tx.origin != "installment":
        raise LookupError(f"Installment transaction {tx_id} not found")
    tx.status = "confirmed"
    db.commit()
    db.refresh(tx)
    return tx
