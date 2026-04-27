import json
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.deps import get_db
from app.services import projection as svc

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/projecao", tags=["projection"])


def _next_month(d: date) -> date:
    if d.month == 12:
        return date(d.year + 1, 1, 1)
    return date(d.year, d.month + 1, 1)


@router.get("", response_class=HTMLResponse)
def projection_view(
    request: Request,
    db: Session = Depends(get_db),
    months: int = 6,
) -> HTMLResponse:
    months = max(3, min(months, 12))
    today = date.today()
    start = _next_month(today)

    rows = svc.project_months(db, start=start, months=months)
    ledger = svc.ledger_for_month(db, year=start.year, month=start.month)

    chart = {
        "labels": [f"{r['year']}-{r['month']:02d}" for r in rows],
        "grand": [float(r["grand_total"]) for r in rows],
        "fixed": [float(r["fixed_total"]) for r in rows],
        "installments": [float(r["installments_total"]) for r in rows],
    }

    total_ledger = sum((r["amount"] for r in ledger), start=0)

    return templates.TemplateResponse(
        request, "projection/index.html",
        {
            "active_nav": "projection",
            "page_title": "Projeção",
            "months": months,
            "rows": rows,
            "ledger": ledger,
            "ledger_total": total_ledger,
            "chart_json": json.dumps(chart),
            "target_year": start.year,
            "target_month": start.month,
        },
    )
