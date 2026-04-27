from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Category, Source
from app.services import transactions as svc

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/lancamentos", tags=["transactions"])


@router.get("", response_class=HTMLResponse)
def list_view(
    request: Request,
    db: Session = Depends(get_db),
    year: int | None = None,
    month: int | None = None,
    source_id: int | None = None,
    category_id: int | None = None,
    text: str | None = None,
) -> HTMLResponse:
    today = date.today()
    effective_year = year or today.year
    effective_month = month or today.month
    items = svc.list_all(
        db, year=effective_year, month=effective_month,
        source_id=source_id, category_id=category_id, text=text or None,
    )
    sources = db.query(Source).filter(Source.archived.is_(False)).all()
    categories = db.query(Category).filter(Category.archived.is_(False)).all()
    return templates.TemplateResponse(
        request, "transactions/list.html",
        {
            "active_nav": "transactions",
            "page_title": "Lançamentos",
            "items": items,
            "sources": sources,
            "categories": categories,
            "filters": {
                "year": effective_year, "month": effective_month,
                "source_id": source_id, "category_id": category_id, "text": text,
            },
        },
    )


@router.get("/novo", response_class=HTMLResponse)
def new_view(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    sources = db.query(Source).filter(Source.archived.is_(False)).all()
    categories = db.query(Category).filter(Category.archived.is_(False)).all()
    return templates.TemplateResponse(
        request, "transactions/new.html",
        {
            "active_nav": "transactions",
            "page_title": "Novo lançamento",
            "sources": sources,
            "categories": categories,
            "today": date.today().isoformat(),
        },
    )


@router.post("/novo")
def create_view(
    db: Session = Depends(get_db),
    description: str = Form(...),
    amount: str = Form(...),
    date_iso: str = Form(..., alias="date"),
    source_id: int = Form(...),
    category_id: int = Form(...),
    payment_mode: str = Form(...),
    type: str = Form("expense"),
    note: str = Form(""),
):
    try:
        amount_decimal = Decimal(amount.replace(",", "."))
    except InvalidOperation as e:
        raise HTTPException(status_code=400, detail="Valor inválido") from e
    if amount_decimal <= 0:
        raise HTTPException(status_code=400, detail="Valor deve ser maior que zero")
    svc.create(db, {
        "description": description,
        "amount": amount_decimal,
        "date": date.fromisoformat(date_iso),
        "source_id": source_id,
        "category_id": category_id,
        "payment_mode": payment_mode,
        "type": type,
        "note": note or None,
    })
    return RedirectResponse("/lancamentos", status_code=303)


@router.get("/{tx_id}/editar", response_class=HTMLResponse)
def edit_view(tx_id: int, request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    try:
        tx = svc.get(db, tx_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    sources = db.query(Source).filter(Source.archived.is_(False)).all()
    categories = db.query(Category).filter(Category.archived.is_(False)).all()
    return templates.TemplateResponse(
        request, "transactions/edit.html",
        {
            "active_nav": "transactions",
            "page_title": f"Editar · {tx.description[:30]}",
            "tx": tx,
            "sources": sources,
            "categories": categories,
        },
    )


@router.post("/{tx_id}/editar")
def update_view(
    tx_id: int,
    db: Session = Depends(get_db),
    description: str = Form(...),
    amount: str = Form(...),
    date_iso: str = Form(..., alias="date"),
    source_id: int = Form(...),
    category_id: int = Form(...),
    payment_mode: str = Form(...),
    type: str = Form("expense"),
    note: str = Form(""),
):
    try:
        amount_decimal = Decimal(amount.replace(",", "."))
    except InvalidOperation as e:
        raise HTTPException(status_code=400, detail="Valor inválido") from e
    try:
        svc.update(db, tx_id, {
            "description": description,
            "amount": amount_decimal,
            "date": date.fromisoformat(date_iso),
            "source_id": source_id,
            "category_id": category_id,
            "payment_mode": payment_mode,
            "type": type,
            "note": note or None,
        })
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return RedirectResponse("/lancamentos", status_code=303)


@router.post("/{tx_id}/delete")
def delete_view(tx_id: int, db: Session = Depends(get_db)):
    try:
        svc.delete(db, tx_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return RedirectResponse("/lancamentos", status_code=303)
