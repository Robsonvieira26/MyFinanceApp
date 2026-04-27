import json
from datetime import date
from decimal import Decimal
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.deps import get_db
from app.services import reports as svc

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/relatorios", tags=["reports"])


def _decimal_list(values: list[Decimal]) -> list[float]:
    return [float(v) for v in values]


@router.get("", response_class=HTMLResponse)
def reports_view(
    request: Request,
    db: Session = Depends(get_db),
    months: int = 6,
) -> HTMLResponse:
    months = max(3, min(months, 24))
    today = date.today()
    labels = svc.month_labels(today, months=months)
    totals = svc.monthly_totals(db, up_to=today, months=months)
    breakdown = svc.category_breakdown_by_month(db, up_to=today, months=months)

    chart_totals = {
        "labels": labels,
        "expense": [float(row["total_expense"]) for row in totals],
        "income": [float(row["total_income"]) for row in totals],
    }
    chart_breakdown = {
        "labels": labels,
        "datasets": [
            {"label": cat, "data": _decimal_list(vals)}
            for cat, vals in breakdown.items()
        ],
    }

    return templates.TemplateResponse(
        request, "reports/index.html",
        {
            "active_nav": "reports",
            "page_title": "Relatórios",
            "months": months,
            "chart_totals_json": json.dumps(chart_totals),
            "chart_breakdown_json": json.dumps(chart_breakdown),
        },
    )
