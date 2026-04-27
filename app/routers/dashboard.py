from calendar import monthrange
from datetime import date
from decimal import Decimal
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.deps import get_db
from app.services import dashboard as svc

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(tags=["dashboard"])


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

    total_spent = overview["total_expense"]
    income = overview["total_income"]
    projected_balance = income - total_spent

    days_total = monthrange(y, m)[1]
    day_today = today.day if (today.year == y and today.month == m) else days_total
    burn_per_day = (
        (total_spent / Decimal(day_today)).quantize(Decimal("0.01"))
        if day_today > 0 else Decimal("0.00")
    )

    return templates.TemplateResponse(
        request, "dashboard.html",
        {
            "active_nav": "dashboard",
            "page_title": "Dashboard",
            "year": y, "month": m,
            "overview": overview,
            "top_categories": top_cats,
            "sources": sources,
            "total_spent": total_spent,
            "income": income,
            "projected_balance": projected_balance,
            "burn_per_day": burn_per_day,
            "today": today,
        },
    )
