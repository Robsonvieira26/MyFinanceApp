from calendar import monthrange
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import Source, Transaction
from app.services.fatura import fatura_due_month

_MONTHS = ["jan", "fev", "mar", "abr", "mai", "jun",
           "jul", "ago", "set", "out", "nov", "dez"]


def billing_month_due_date(
    billing_year: int, billing_month: int, closing_day: int, due_day: int
) -> date:
    """Compute the actual payment due date for a billing reference month.

    Uses closing_day+1 as a representative purchase date within the billing
    cycle, then delegates to fatura_due_month.
    """
    ref_day = closing_day + 1
    last_day = monthrange(billing_year, billing_month)[1]
    if ref_day > last_day:
        nm = billing_month % 12 + 1
        ny = billing_year + (1 if billing_month == 12 else 0)
        ref = date(ny, nm, 1)
    else:
        ref = date(billing_year, billing_month, ref_day)
    return fatura_due_month(ref, closing_day, due_day)


def _settlement_exists(
    db: Session, credit_source_id: int, due_date: date
) -> Transaction | None:
    return db.execute(
        select(Transaction)
        .options(joinedload(Transaction.source))
        .where(
            Transaction.origin == "fatura_settlement",
            Transaction.origin_ref_id == credit_source_id,
            func.extract("year", Transaction.date) == due_date.year,
            func.extract("month", Transaction.date) == due_date.month,
        )
    ).scalar_one_or_none()


def get_fatura_totals(db: Session) -> list[dict]:
    """For each credit card source, list billing months with totals and settlement status."""
    credit_sources = (
        db.query(Source)
        .filter(
            Source.kind != "debit",
            Source.closing_day.isnot(None),
            Source.due_day.isnot(None),
            Source.archived.is_(False),
        )
        .all()
    )

    results = []
    for src in credit_sources:
        rows = db.execute(
            select(
                func.extract("year", Transaction.date).label("yr"),
                func.extract("month", Transaction.date).label("mo"),
                func.sum(Transaction.amount).label("total"),
            )
            .where(
                Transaction.source_id == src.id,
                Transaction.payment_mode == "credit",
                Transaction.type == "expense",
            )
            .group_by("yr", "mo")
            .order_by("yr", "mo")
        ).all()

        for row in rows:
            yr, mo = int(row.yr), int(row.mo)
            total = Decimal(str(row.total)).quantize(Decimal("0.01"))
            due = billing_month_due_date(yr, mo, src.closing_day, src.due_day)
            settlement = _settlement_exists(db, src.id, due)
            results.append({
                "source": src,
                "billing_year": yr,
                "billing_month": mo,
                "billing_label": f"{_MONTHS[mo - 1]}/{yr}",
                "total": total,
                "due_date": due,
                "settlement": settlement,
                "is_paid": settlement is not None,
            })

    results.sort(key=lambda r: (r["billing_year"], r["billing_month"], r["source"].name))
    return results


def create_settlement(
    db: Session,
    credit_source_id: int,
    billing_year: int,
    billing_month: int,
    checking_source_id: int,
    category_id: int,
) -> Transaction:
    src = db.get(Source, credit_source_id)
    if src is None:
        raise LookupError(f"Cartão {credit_source_id} não encontrado")

    start = date(billing_year, billing_month, 1)
    end = date(billing_year, billing_month, monthrange(billing_year, billing_month)[1])
    total_raw = db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.source_id == credit_source_id,
            Transaction.payment_mode == "credit",
            Transaction.type == "expense",
            Transaction.date >= start,
            Transaction.date <= end,
        )
    ).scalar()
    total = Decimal(str(total_raw)).quantize(Decimal("0.01"))

    due = billing_month_due_date(billing_year, billing_month, src.closing_day, src.due_day)
    desc = f"Fatura {src.name} {_MONTHS[billing_month - 1]}/{billing_year}"

    tx = Transaction(
        description=desc,
        amount=total,
        date=due,
        source_id=checking_source_id,
        category_id=category_id,
        payment_mode="debit",
        type="expense",
        origin="fatura_settlement",
        origin_ref_id=credit_source_id,
        status="confirmed",
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx
