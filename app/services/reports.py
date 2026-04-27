from calendar import monthrange
from datetime import date
from decimal import Decimal
from typing import TypedDict

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Category, Transaction


class MonthlyRow(TypedDict):
    year: int
    month: int
    total_expense: Decimal
    total_income: Decimal


def _iter_months_back(up_to: date, months: int) -> list[tuple[int, int]]:
    anchor_year = up_to.year
    anchor_month = up_to.month
    result: list[tuple[int, int]] = []
    for i in range(months - 1, -1, -1):
        idx = anchor_month - 1 - i
        y = anchor_year + idx // 12
        m = idx % 12 + 1
        result.append((y, m))
    return result


def month_labels(up_to: date, *, months: int) -> list[str]:
    return [f"{y}-{m:02d}" for y, m in _iter_months_back(up_to, months)]


def monthly_totals(
    db: Session, *, up_to: date, months: int = 6
) -> list[MonthlyRow]:
    periods = _iter_months_back(up_to, months)
    result: list[MonthlyRow] = []
    for y, m in periods:
        end_day = monthrange(y, m)[1]
        start, end = date(y, m, 1), date(y, m, end_day)
        rows = db.execute(
            select(
                Transaction.type,
                func.coalesce(func.sum(Transaction.amount), 0),
            )
            .where(Transaction.date >= start, Transaction.date <= end)
            .where(Transaction.status == "confirmed")
            .group_by(Transaction.type)
        ).all()
        expense = Decimal("0.00")
        income = Decimal("0.00")
        for t, total in rows:
            if t == "income":
                income = Decimal(total).quantize(Decimal("0.01"))
            else:
                expense = Decimal(total).quantize(Decimal("0.01"))
        result.append({
            "year": y, "month": m,
            "total_expense": expense, "total_income": income,
        })
    return result


def category_breakdown_by_month(
    db: Session, *, up_to: date, months: int = 6
) -> dict[str, list[Decimal]]:
    """Returns dict[category_name] = [value_month_1, ..., value_month_N]."""
    periods = _iter_months_back(up_to, months)
    categories = db.query(Category).all()
    result = {cat.name: [Decimal("0.00")] * months for cat in categories}

    for idx, (y, m) in enumerate(periods):
        end_day = monthrange(y, m)[1]
        start, end = date(y, m, 1), date(y, m, end_day)
        rows = db.execute(
            select(Category.name, func.coalesce(func.sum(Transaction.amount), 0))
            .join(Transaction, Transaction.category_id == Category.id)
            .where(Transaction.date >= start, Transaction.date <= end)
            .where(Transaction.status == "confirmed", Transaction.type == "expense")
            .group_by(Category.name)
        ).all()
        for name, total in rows:
            result[name][idx] = Decimal(total).quantize(Decimal("0.01"))

    return {k: v for k, v in result.items() if any(x > 0 for x in v)}
