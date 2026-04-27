from decimal import Decimal, InvalidOperation
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Category, Source
from app.services import budgets as bud_svc
from app.services import sources as src_svc

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/config", tags=["config"])


@router.get("/sistema", response_class=HTMLResponse)
def system_view(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    total_budget = bud_svc.get_total(db) or Decimal("0.00")
    return templates.TemplateResponse(
        request, "config/system.html",
        {
            "active_nav": "system",
            "page_title": "Sistema",
            "total_budget": total_budget,
        },
    )


@router.post("/sistema/budget")
def set_total_budget(
    db: Session = Depends(get_db),
    amount: str = Form(...),
):
    try:
        val = Decimal(amount.replace(",", "."))
    except InvalidOperation as e:
        raise HTTPException(status_code=400, detail="Valor inválido") from e
    bud_svc.set_total(db, val)
    return RedirectResponse("/config/sistema", status_code=303)


@router.get("/categorias", response_class=HTMLResponse)
def categories_view(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    cats = db.query(Category).filter(Category.archived.is_(False)).order_by(Category.name).all()
    budgets_map = bud_svc.get_by_category(db)
    return templates.TemplateResponse(
        request, "config/categories.html",
        {
            "active_nav": "categories",
            "page_title": "Categorias",
            "categories": cats,
            "budgets_map": budgets_map,
        },
    )


@router.post("/categorias/{cat_id}/budget")
def set_cat_budget(
    cat_id: int,
    db: Session = Depends(get_db),
    amount: str = Form(...),
):
    try:
        val = Decimal(amount.replace(",", "."))
    except InvalidOperation as e:
        raise HTTPException(status_code=400, detail="Valor inválido") from e
    if val == 0:
        bud_svc.delete_category(db, cat_id)
    else:
        bud_svc.set_category(db, category_id=cat_id, amount=val)
    return RedirectResponse("/config/categorias", status_code=303)


@router.get("/fontes", response_class=HTMLResponse)
def sources_view(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    sources = src_svc.list_all(db, include_archived=True)
    return templates.TemplateResponse(
        request, "config/sources.html",
        {
            "active_nav": "sources",
            "page_title": "Fontes",
            "sources": sources,
        },
    )


@router.post("/fontes/novo")
def create_source(
    db: Session = Depends(get_db),
    slug: str = Form(...),
    name: str = Form(...),
    kind: str = Form(...),
    closing_day: str = Form(""),
    due_day: str = Form(""),
):
    if db.query(Source).filter_by(slug=slug).first():
        raise HTTPException(status_code=400, detail="Slug já existe")
    cd = int(closing_day) if closing_day.strip() else None
    dd = int(due_day) if due_day.strip() else None
    src_svc.create(db, slug=slug, name=name, kind=kind, closing_day=cd, due_day=dd)
    return RedirectResponse("/config/fontes", status_code=303)


@router.post("/fontes/{source_id}/billing")
def update_source_billing(
    source_id: int,
    db: Session = Depends(get_db),
    closing_day: str = Form(""),
    due_day: str = Form(""),
):
    cd = int(closing_day) if closing_day.strip() else None
    dd = int(due_day) if due_day.strip() else None
    src_svc.update_billing(db, source_id, closing_day=cd, due_day=dd)
    return RedirectResponse("/config/fontes", status_code=303)


@router.post("/fontes/{source_id}/archive")
def archive_source(source_id: int, db: Session = Depends(get_db)):
    src_svc.archive(db, source_id)
    return RedirectResponse("/config/fontes", status_code=303)


@router.post("/fontes/{source_id}/unarchive")
def unarchive_source(source_id: int, db: Session = Depends(get_db)):
    src_svc.unarchive(db, source_id)
    return RedirectResponse("/config/fontes", status_code=303)


@router.post("/categorias/novo")
def create_category(
    db: Session = Depends(get_db),
    slug: str = Form(...),
    name: str = Form(...),
    icon: str = Form(""),
):
    if db.query(Category).filter_by(slug=slug).first():
        raise HTTPException(status_code=400, detail="Slug já existe")
    cat = Category(slug=slug, name=name, icon=icon or None)
    db.add(cat)
    db.commit()
    return RedirectResponse("/config/categorias", status_code=303)
