from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Category, Source
from app.services import fixed as svc

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/fixos", tags=["fixed"])


@router.get("", response_class=HTMLResponse)
def list_view(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    rules = svc.list_rules(db, include_archived=True)
    today = date.today()
    occurrences = svc.project_month(db, year=today.year, month=today.month)
    return templates.TemplateResponse(
        request, "fixed/list.html",
        {
            "active_nav": "fixed",
            "page_title": "Gastos fixos",
            "rules": rules,
            "occurrences": occurrences,
            "year": today.year,
            "month": today.month,
        },
    )


@router.get("/novo", response_class=HTMLResponse)
def new_view(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    sources = db.query(Source).filter(Source.archived.is_(False)).all()
    categories = db.query(Category).filter(Category.archived.is_(False)).all()
    return templates.TemplateResponse(
        request, "fixed/new.html",
        {
            "active_nav": "fixed",
            "page_title": "Novo fixo",
            "sources": sources,
            "categories": categories,
            "today": date.today().isoformat(),
        },
    )


@router.post("/novo")
def create_view(
    db: Session = Depends(get_db),
    description: str = Form(...),
    expected_amount: str = Form(...),
    recurrence: str = Form(...),
    source_id: int = Form(...),
    category_id: int = Form(...),
    payment_mode: str = Form(...),
    type: str = Form("expense"),
    active_from: str = Form(...),
    active_until: str = Form(""),
    day_of_month: str = Form(""),
    day_of_week: str = Form(""),
    anchor_month: str = Form(""),
    interval_months: str = Form(""),
):
    try:
        amt = Decimal(expected_amount.replace(",", "."))
    except InvalidOperation as e:
        raise HTTPException(status_code=400, detail="Valor inválido") from e

    data = {
        "description": description,
        "expected_amount": amt,
        "recurrence": recurrence,
        "source_id": source_id,
        "category_id": category_id,
        "payment_mode": payment_mode,
        "type": type,
        "active_from": date.fromisoformat(active_from),
        "active_until": date.fromisoformat(active_until) if active_until else None,
        "day_of_month": int(day_of_month) if day_of_month else None,
        "day_of_week": int(day_of_week) if day_of_week else None,
        "anchor_month": int(anchor_month) if anchor_month else None,
        "interval_months": int(interval_months) if interval_months else None,
    }
    try:
        svc.create_rule(db, data)
    except (LookupError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return RedirectResponse("/fixos", status_code=303)


@router.post("/{rule_id}/archive")
def archive_view(rule_id: int, db: Session = Depends(get_db)):
    try:
        svc.archive_rule(db, rule_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return RedirectResponse("/fixos", status_code=303)


@router.post("/confirm")
def confirm_view(
    db: Session = Depends(get_db),
    rule_id: int = Form(...),
    occ_date: str = Form(...),
    actual_amount: str = Form(...),
):
    try:
        amt = Decimal(actual_amount.replace(",", "."))
    except InvalidOperation as e:
        raise HTTPException(status_code=400, detail="Valor inválido") from e
    try:
        svc.confirm_occurrence(
            db, rule_id=rule_id, occ_date=date.fromisoformat(occ_date), actual_amount=amt
        )
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return RedirectResponse("/fixos", status_code=303)
