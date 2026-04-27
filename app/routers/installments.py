from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Category, Source, Transaction
from app.services import installments as svc

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/parcelados", tags=["installments"])


@router.get("", response_class=HTMLResponse)
def list_view(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    plans = svc.list_plans(db, active_only=False)
    return templates.TemplateResponse(
        request, "installments/list.html",
        {"active_nav": "installments", "page_title": "Parcelados", "plans": plans},
    )


@router.get("/novo", response_class=HTMLResponse)
def new_view(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    sources = db.query(Source).filter(
        Source.archived.is_(False), Source.closing_day.isnot(None)
    ).all()
    categories = db.query(Category).filter(Category.archived.is_(False)).all()
    return templates.TemplateResponse(
        request, "installments/new.html",
        {
            "active_nav": "installments",
            "page_title": "Novo parcelamento",
            "sources": sources,
            "categories": categories,
            "today": date.today().isoformat(),
        },
    )


@router.post("/novo")
def create_view(
    db: Session = Depends(get_db),
    description: str = Form(...),
    installments_count: int = Form(...),
    first_purchase_date: str = Form(...),
    source_id: int = Form(...),
    category_id: int = Form(...),
    input_mode: str = Form(...),
    total_amount: str = Form(""),
    installment_amount: str = Form(""),
):
    data = {
        "description": description,
        "installments_count": installments_count,
        "first_purchase_date": date.fromisoformat(first_purchase_date),
        "source_id": source_id,
        "category_id": category_id,
        "input_mode": input_mode,
    }
    try:
        if input_mode == "total":
            data["total_amount"] = Decimal(total_amount.replace(",", "."))
        else:
            data["installment_amount"] = Decimal(installment_amount.replace(",", "."))
    except InvalidOperation as e:
        raise HTTPException(status_code=400, detail="Valor inválido") from e
    try:
        svc.create_plan(db, data)
    except (LookupError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return RedirectResponse("/parcelados", status_code=303)


@router.post("/{plan_id}/delete")
def delete_view(plan_id: int, db: Session = Depends(get_db)):
    try:
        svc.delete_plan(db, plan_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return RedirectResponse("/parcelados", status_code=303)


@router.get("/{plan_id}", response_class=HTMLResponse)
def detail_view(plan_id: int, request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    try:
        plan = svc.get_plan(db, plan_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    installments = (
        db.query(Transaction)
        .filter(Transaction.origin_ref_id == plan.id, Transaction.origin == "installment")
        .order_by(Transaction.date)
        .all()
    )
    return templates.TemplateResponse(
        request, "installments/detail.html",
        {
            "active_nav": "installments",
            "page_title": f"Parcelamento · {plan.description}",
            "plan": plan,
            "installments": installments,
        },
    )


@router.post("/tx/{tx_id}/confirm")
def confirm_installment_view(tx_id: int, db: Session = Depends(get_db)):
    try:
        tx = svc.confirm_installment(db, tx_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return RedirectResponse(f"/parcelados/{tx.origin_ref_id}", status_code=303)
