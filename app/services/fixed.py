from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.models import FixedRule, Transaction
from app.services.fixed_projection import project_rule


def create_rule(db: Session, data: dict[str, Any]) -> FixedRule:
    rule = FixedRule(**data)
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def list_rules(db: Session, *, include_archived: bool = False) -> list[FixedRule]:
    q = db.query(FixedRule)
    if not include_archived:
        q = q.filter(FixedRule.archived.is_(False))
    return q.order_by(FixedRule.description).all()


def get_rule(db: Session, rule_id: int) -> FixedRule:
    r = db.get(FixedRule, rule_id)
    if r is None:
        raise LookupError(f"FixedRule {rule_id} not found")
    return r


def archive_rule(db: Session, rule_id: int) -> FixedRule:
    r = get_rule(db, rule_id)
    r.archived = True
    db.commit()
    db.refresh(r)
    return r


def project_month(db: Session, *, year: int, month: int) -> list[dict[str, Any]]:
    from calendar import monthrange

    start = date(year, month, 1)
    end = date(year, month, monthrange(year, month)[1])

    rules = list_rules(db, include_archived=False)
    results: list[dict[str, Any]] = []
    for rule in rules:
        for occ_date in project_rule(rule, start=start, end=end):
            confirmed = (
                db.query(Transaction)
                .filter(
                    Transaction.origin == "fixed",
                    Transaction.origin_ref_id == rule.id,
                    Transaction.date == occ_date,
                    Transaction.status == "confirmed",
                )
                .first()
            )
            results.append({
                "rule_id": rule.id,
                "description": rule.description,
                "date": occ_date,
                "expected_amount": rule.expected_amount,
                "actual_amount": confirmed.amount if confirmed else None,
                "confirmed_tx_id": confirmed.id if confirmed else None,
                "source_id": rule.source_id,
                "category_id": rule.category_id,
                "payment_mode": rule.payment_mode,
                "type": rule.type,
            })
    return results


def confirm_occurrence(
    db: Session,
    *,
    rule_id: int,
    occ_date: date,
    actual_amount: Decimal,
) -> Transaction:
    rule = get_rule(db, rule_id)
    existing = (
        db.query(Transaction)
        .filter(
            Transaction.origin == "fixed",
            Transaction.origin_ref_id == rule.id,
            Transaction.date == occ_date,
        )
        .first()
    )
    if existing:
        existing.amount = actual_amount
        existing.status = "confirmed"
        db.commit()
        db.refresh(existing)
        return existing
    tx = Transaction(
        description=rule.description,
        amount=actual_amount,
        date=occ_date,
        source_id=rule.source_id,
        category_id=rule.category_id,
        payment_mode=rule.payment_mode,
        type=rule.type,
        origin="fixed",
        origin_ref_id=rule.id,
        status="confirmed",
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx
