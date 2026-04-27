from calendar import monthrange
from datetime import date
from decimal import Decimal
from typing import TypedDict

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Category, Source, Transaction


class CategoryRow(TypedDict):
    category_id: int
    name: str
    total: Decimal
    source_name: str | None
    source_kind: str | None


class SourceRow(TypedDict):
    source_id: int
    slug: str
    name: str
    kind: str
    total: Decimal


class MonthOverview(TypedDict):
    year: int
    month: int
    total_expense: Decimal
    total_income: Decimal
    count: int


def _month_bounds(year: int, month: int) -> tuple[date, date]:
    end_day = monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, end_day)


def month_overview(db: Session, *, year: int, month: int) -> MonthOverview:
    start, end = _month_bounds(year, month)
    totals = db.execute(
        select(
            Transaction.type,
            func.coalesce(func.sum(Transaction.amount), 0),
            func.count(Transaction.id),
        )
        .where(Transaction.date >= start, Transaction.date <= end)
        .where(Transaction.status == "confirmed")
        .group_by(Transaction.type)
    ).all()
    expense = Decimal("0.00")
    income = Decimal("0.00")
    count = 0
    for t, total, n in totals:
        count += n
        if t == "income":
            income = Decimal(total).quantize(Decimal("0.01"))
        else:
            expense = Decimal(total).quantize(Decimal("0.01"))
    return {
        "year": year, "month": month,
        "total_expense": expense, "total_income": income, "count": count,
    }


def top_categories(
    db: Session, *, year: int, month: int, limit: int = 5
) -> list[CategoryRow]:
    start, end = _month_bounds(year, month)
    rows = db.execute(
        select(
            Category.id, Category.name,
            func.coalesce(func.sum(Transaction.amount), 0).label("total"),
        )
        .join(Transaction, Transaction.category_id == Category.id)
        .where(Transaction.date >= start, Transaction.date <= end)
        .where(Transaction.status == "confirmed", Transaction.type == "expense")
        .group_by(Category.id, Category.name)
        .order_by(func.sum(Transaction.amount).desc())
        .limit(limit)
    ).all()

    result: list[CategoryRow] = []
    for row in rows:
        top_src = db.execute(
            select(Source.name, Source.kind)
            .join(Transaction, Transaction.source_id == Source.id)
            .where(
                Transaction.category_id == row.id,
                Transaction.date >= start,
                Transaction.date <= end,
                Transaction.status == "confirmed",
                Transaction.type == "expense",
            )
            .group_by(Source.id, Source.name, Source.kind)
            .order_by(func.sum(Transaction.amount).desc())
            .limit(1)
        ).first()
        result.append({
            "category_id": row.id,
            "name": row.name,
            "total": Decimal(row.total).quantize(Decimal("0.01")),
            "source_name": top_src.name if top_src else None,
            "source_kind": top_src.kind if top_src else None,
        })
    return result


def by_source(db: Session, *, year: int, month: int) -> list[SourceRow]:
    start, end = _month_bounds(year, month)
    rows = db.execute(
        select(
            Source.id, Source.slug, Source.name, Source.kind,
            func.coalesce(func.sum(Transaction.amount), 0).label("total"),
        )
        .join(Transaction, Transaction.source_id == Source.id)
        .where(Transaction.date >= start, Transaction.date <= end)
        .where(Transaction.status == "confirmed", Transaction.type == "expense")
        .group_by(Source.id, Source.slug, Source.name, Source.kind)
        .order_by(func.sum(Transaction.amount).desc())
    ).all()
    return [
        {"source_id": row.id, "slug": row.slug, "name": row.name,
         "kind": row.kind,
         "total": Decimal(row.total).quantize(Decimal("0.01"))}
        for row in rows
    ]
