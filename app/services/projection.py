from calendar import monthrange
from datetime import date
from decimal import Decimal
from typing import Any, TypedDict

from sqlalchemy.orm import Session

from app.models import FixedRule, Transaction
from app.services.fixed_projection import project_rule


class MonthSummary(TypedDict):
    year: int
    month: int
    fixed_total: Decimal
    installments_total: Decimal
    grand_total: Decimal


def _month_bounds(year: int, month: int) -> tuple[date, date]:
    return date(year, month, 1), date(year, month, monthrange(year, month)[1])


def _iter_months(start: date, months: int) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    y, m = start.year, start.month
    for _ in range(months):
        result.append((y, m))
        m += 1
        if m > 12:
            m = 1
            y += 1
    return result


def project_months(
    db: Session, *, start: date, months: int
) -> list[MonthSummary]:
    periods = _iter_months(start, months)
    rules = db.query(FixedRule).filter(FixedRule.archived.is_(False)).all()
    result: list[MonthSummary] = []

    for y, m in periods:
        month_start, month_end = _month_bounds(y, m)

        fixed_total = Decimal("0.00")
        for rule in rules:
            occs = project_rule(rule, start=month_start, end=month_end)
            fixed_total += rule.expected_amount * len(occs)
        fixed_total = fixed_total.quantize(Decimal("0.01"))

        inst_total_q = db.query(
            Transaction.amount
        ).filter(
            Transaction.origin == "installment",
            Transaction.date >= month_start,
            Transaction.date <= month_end,
        ).all()
        inst_total = sum((row.amount for row in inst_total_q), Decimal("0.00")).quantize(
            Decimal("0.01")
        )

        result.append({
            "year": y, "month": m,
            "fixed_total": fixed_total,
            "installments_total": inst_total,
            "grand_total": (fixed_total + inst_total).quantize(Decimal("0.01")),
        })

    return result


def ledger_for_month(db: Session, *, year: int, month: int) -> list[dict[str, Any]]:
    start, end = _month_bounds(year, month)
    result: list[dict[str, Any]] = []

    rules = db.query(FixedRule).filter(FixedRule.archived.is_(False)).all()
    for rule in rules:
        for occ in project_rule(rule, start=start, end=end):
            result.append({
                "kind": "fixed",
                "description": rule.description,
                "date": occ,
                "amount": rule.expected_amount,
                "source": rule.source.name,
                "category": rule.category.name,
                "ref_id": rule.id,
            })

    installments = (
        db.query(Transaction)
        .filter(
            Transaction.origin == "installment",
            Transaction.date >= start, Transaction.date <= end,
        )
        .all()
    )
    for tx in installments:
        result.append({
            "kind": "installment",
            "description": tx.description,
            "date": tx.date,
            "amount": tx.amount,
            "source": tx.source.name,
            "category": tx.category.name,
            "ref_id": tx.id,
        })

    result.sort(key=lambda r: (r["date"], r["kind"]))
    return result
