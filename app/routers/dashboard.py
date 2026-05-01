from datetime import date
from decimal import Decimal
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Transaction
from app.services import alerts as alerts_svc
from app.services import budgets as bud_svc
from app.services import dashboard as svc
from app.services import installments as inst_svc

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(tags=["dashboard"])


def _days_in_month(year: int, month: int) -> int:
    from calendar import monthrange
    return monthrange(year, month)[1]


@router.get("/", response_class=HTMLResponse)
def dashboard_view(
    request: Request,
    db: Session = Depends(get_db),
    year: int | None = None,
    month: int | None = None,
) -> HTMLResponse:
    today = date.today()
    y = year or today.year
    m = month or today.month

    overview = svc.month_overview(db, year=y, month=m)
    top_cats = svc.top_categories(db, year=y, month=m, limit=5)
    sources = svc.by_source(db, year=y, month=m)
    alerts = alerts_svc.evaluate(db, year=y, month=m)
    total_budget = bud_svc.get_total(db) or Decimal("0.00")

    plans_raw = inst_svc.list_plans(db, active_only=True)
    active_plans = []
    for p in plans_raw[:5]:
        paid = db.query(Transaction).filter(
            Transaction.origin == "installment",
            Transaction.origin_ref_id == p.id,
            Transaction.date <= today,
        ).count()
        active_plans.append({
            "description": p.description,
            "current": paid,
            "total": p.installments_count,
            "amount": p.installment_amount,
        })

    total_spent = overview["total_expense"]
    income = overview["total_income"]
    projected_balance = income - total_spent

    days_total = _days_in_month(y, m)
    day_today = today.day if (today.year == y and today.month == m) else days_total
    burn_per_day = (
        (total_spent / Decimal(day_today)).quantize(Decimal("0.01"))
        if day_today > 0 else Decimal("0.00")
    )

    budget_ratio = (
        float((total_spent / total_budget) * 100) if total_budget > 0 else 0
    )

    prev_y, prev_m = (y - 1, 12) if m == 1  else (y, m - 1)
    next_y, next_m = (y + 1, 1)  if m == 12 else (y, m + 1)
    is_current = (y == today.year and m == today.month)

    return templates.TemplateResponse(
        request, "dashboard.html",
        {
            "active_nav": "dashboard",
            "page_title": "Dashboard",
            "year": y, "month": m,
            "overview": overview,
            "top_categories": top_cats,
            "sources": sources,
            "alerts": alerts,
            "total_spent": total_spent,
            "total_budget": total_budget,
            "budget_ratio": budget_ratio,
            "income": income,
            "projected_balance": projected_balance,
            "burn_per_day": burn_per_day,
            "today": today,
            "active_plans": active_plans,
            "prev_y": prev_y, "prev_m": prev_m,
            "next_y": next_y, "next_m": next_m,
            "is_current": is_current,
        },
    )
