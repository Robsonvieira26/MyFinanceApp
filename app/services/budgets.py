from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import Budget


def list_all(db: Session) -> list[Budget]:
    return db.query(Budget).all()


def set_total(db: Session, amount: Decimal) -> Budget:
    existing = db.query(Budget).filter_by(scope="total", category_id=None).first()
    if existing:
        existing.amount = amount
        db.commit()
        db.refresh(existing)
        return existing
    b = Budget(scope="total", category_id=None, amount=amount)
    db.add(b)
    db.commit()
    db.refresh(b)
    return b


def set_category(db: Session, *, category_id: int, amount: Decimal) -> Budget:
    existing = db.query(Budget).filter_by(scope="category", category_id=category_id).first()
    if existing:
        existing.amount = amount
        db.commit()
        db.refresh(existing)
        return existing
    b = Budget(scope="category", category_id=category_id, amount=amount)
    db.add(b)
    db.commit()
    db.refresh(b)
    return b


def get_total(db: Session) -> Decimal | None:
    b = db.query(Budget).filter_by(scope="total", category_id=None).first()
    return b.amount if b else None


def get_by_category(db: Session) -> dict[int, Decimal]:
    rows = db.query(Budget).filter(Budget.scope == "category").all()
    return {b.category_id: b.amount for b in rows if b.category_id is not None}


def delete_category(db: Session, category_id: int) -> None:
    existing = db.query(Budget).filter_by(scope="category", category_id=category_id).first()
    if existing:
        db.delete(existing)
        db.commit()
