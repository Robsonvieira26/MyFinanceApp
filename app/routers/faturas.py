from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from sqlalchemy.orm import joinedload

from app.deps import get_db
from app.models import Category, Source, Transaction
from app.services import fatura_settlement as svc

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/faturas", tags=["faturas"])


@router.get("", response_class=HTMLResponse)
def list_view(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    faturas = svc.get_fatura_totals(db)
    debit_sources = (
        db.query(Source)
        .filter(Source.archived.is_(False), Source.closing_day.is_(None))
        .all()
    )
    categories = db.query(Category).filter(Category.archived.is_(False)).all()
    return templates.TemplateResponse(
        request, "faturas/list.html",
        {
            "active_nav": "faturas",
            "page_title": "Faturas",
            "faturas": faturas,
            "debit_sources": debit_sources,
            "categories": categories,
        },
    )


@router.post("/liquidar")
def liquidar_view(
    db: Session = Depends(get_db),
    credit_source_id: int = Form(...),
    billing_year: int = Form(...),
    billing_month: int = Form(...),
    checking_source_id: int = Form(...),
    category_id: int = Form(...),
):
    try:
        svc.create_settlement(
            db,
            credit_source_id=credit_source_id,
            billing_year=billing_year,
            billing_month=billing_month,
            checking_source_id=checking_source_id,
            category_id=category_id,
        )
    except (LookupError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return RedirectResponse("/faturas", status_code=303)


@router.post("/estornar/{tx_id}")
def estornar_view(tx_id: int, db: Session = Depends(get_db)):
    from app.models import Transaction
    tx = db.get(Transaction, tx_id)
    if tx is None or tx.origin != "fatura_settlement":
        raise HTTPException(status_code=404, detail="Liquidação não encontrada")
    db.delete(tx)
    db.commit()
    return RedirectResponse("/faturas", status_code=303)
