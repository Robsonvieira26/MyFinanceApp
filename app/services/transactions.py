from calendar import monthrange
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models import Transaction


def create(db: Session, data: dict[str, Any]) -> Transaction:
    tx = Transaction(
        origin=data.pop("origin", "manual"),
        status=data.pop("status", "confirmed"),
        **data,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


def list_all(
    db: Session,
    *,
    year: int | None = None,
    month: int | None = None,
    source_id: int | None = None,
    category_id: int | None = None,
    text: str | None = None,
    limit: int | None = None,
) -> list[Transaction]:
    stmt = select(Transaction).options(
        joinedload(Transaction.source),
        joinedload(Transaction.category),
    )
    if year is not None and month is not None:
        start = date(year, month, 1)
        end_day = monthrange(year, month)[1]
        end = date(year, month, end_day)
        stmt = stmt.where(Transaction.date >= start, Transaction.date <= end)
    if source_id is not None:
        stmt = stmt.where(Transaction.source_id == source_id)
    if category_id is not None:
        stmt = stmt.where(Transaction.category_id == category_id)
    if text:
        stmt = stmt.where(Transaction.description.ilike(f"%{text}%"))
    stmt = stmt.order_by(Transaction.date.desc(), Transaction.id.desc())
    if limit is not None:
        stmt = stmt.limit(limit)
    return list(db.execute(stmt).scalars().all())


def get(db: Session, tx_id: int) -> Transaction:
    tx = db.get(Transaction, tx_id)
    if tx is None:
        raise LookupError(f"Transaction {tx_id} not found")
    return tx


def update(db: Session, tx_id: int, data: dict[str, Any]) -> Transaction:
    tx = get(db, tx_id)
    for key, value in data.items():
        if value is None:
            continue
        setattr(tx, key, value)
    db.commit()
    db.refresh(tx)
    return tx


def delete(db: Session, tx_id: int) -> None:
    tx = get(db, tx_id)
    db.delete(tx)
    db.commit()
