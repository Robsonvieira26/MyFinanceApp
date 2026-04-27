from decimal import Decimal
from typing import TypedDict

from sqlalchemy.orm import Session

from app.models import Category
from app.services import budgets as bud_svc
from app.services import dashboard as dash_svc

CATEGORY_THRESHOLD = Decimal("0.80")
TOTAL_THRESHOLD = Decimal("0.90")


class Alert(TypedDict):
    kind: str  # category_threshold | total_threshold
    level: str  # warn | err
    message: str
    pct: float
    ref_id: int | None


def evaluate(db: Session, *, year: int, month: int) -> list[Alert]:
    alerts: list[Alert] = []

    cat_budgets = bud_svc.get_by_category(db)
    if cat_budgets:
        cats = {c.id: c.name for c in db.query(Category).all()}
        top = dash_svc.top_categories(db, year=year, month=month, limit=50)
        spent_by_cat = {row["category_id"]: row["total"] for row in top}
        for cat_id, alvo in cat_budgets.items():
            spent = spent_by_cat.get(cat_id, Decimal("0.00"))
            if alvo <= 0:
                continue
            ratio = Decimal(spent) / alvo
            if ratio >= CATEGORY_THRESHOLD:
                level = "err" if ratio > Decimal("1.0") else "warn"
                alerts.append({
                    "kind": "category_threshold",
                    "level": level,
                    "message": f"{cats.get(cat_id, '?')} — {int(ratio * 100)}% do alvo",
                    "pct": float(ratio * 100),
                    "ref_id": cat_id,
                })

    total_budget = bud_svc.get_total(db)
    if total_budget and total_budget > 0:
        overview = dash_svc.month_overview(db, year=year, month=month)
        ratio = overview["total_expense"] / total_budget
        if ratio >= TOTAL_THRESHOLD:
            level = "err" if ratio > Decimal("1.0") else "warn"
            alerts.append({
                "kind": "total_threshold",
                "level": level,
                "message": f"Orçamento total — {int(ratio * 100)}%",
                "pct": float(ratio * 100),
                "ref_id": None,
            })

    return alerts
