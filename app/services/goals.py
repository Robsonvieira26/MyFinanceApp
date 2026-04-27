from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.models import Goal


def create(db: Session, data: dict[str, Any]) -> Goal:
    g = Goal(**data)
    if g.saved_amount is None:
        g.saved_amount = Decimal("0.00")
    db.add(g)
    db.commit()
    db.refresh(g)
    return g


def get(db: Session, goal_id: int) -> Goal:
    g = db.get(Goal, goal_id)
    if g is None:
        raise LookupError(f"Goal {goal_id} not found")
    return g


def list_all(db: Session, *, include_archived: bool = False) -> list[Goal]:
    q = db.query(Goal)
    if not include_archived:
        q = q.filter(Goal.active.is_(True))
    return q.order_by(Goal.target_date.asc().nullslast(), Goal.id.desc()).all()


def add_progress(db: Session, goal_id: int, amount: Decimal) -> Goal:
    g = get(db, goal_id)
    g.saved_amount = (g.saved_amount or Decimal("0.00")) + amount
    db.commit()
    db.refresh(g)
    return g


def update(db: Session, goal_id: int, data: dict[str, Any]) -> Goal:
    g = get(db, goal_id)
    for k, v in data.items():
        if v is not None:
            setattr(g, k, v)
    db.commit()
    db.refresh(g)
    return g


def archive(db: Session, goal_id: int) -> Goal:
    g = get(db, goal_id)
    g.active = False
    db.commit()
    db.refresh(g)
    return g


def progress_pct(goal: Goal) -> float:
    if goal.target_amount == 0:
        return 0.0
    return float((goal.saved_amount / goal.target_amount) * 100)
