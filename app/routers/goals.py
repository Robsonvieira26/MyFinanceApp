from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.deps import get_db
from app.services import goals as svc

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/metas", tags=["goals"])


@router.get("", response_class=HTMLResponse)
def list_view(request: Request, db: Session = Depends(get_db)) -> HTMLResponse:
    items = svc.list_all(db, include_archived=True)
    return templates.TemplateResponse(
        request, "goals/list.html",
        {
            "active_nav": "goals",
            "page_title": "Metas",
            "goals": items,
            "progress_pct": svc.progress_pct,
        },
    )


@router.get("/nova", response_class=HTMLResponse)
def new_view(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "goals/new.html",
        {"active_nav": "goals", "page_title": "Nova meta"},
    )


@router.post("/nova")
def create_view(
    db: Session = Depends(get_db),
    title: str = Form(...),
    target_amount: str = Form(...),
    target_date: str = Form(""),
    note: str = Form(""),
):
    try:
        amt = Decimal(target_amount.replace(",", "."))
    except InvalidOperation as e:
        raise HTTPException(status_code=400, detail="Valor inválido") from e
    svc.create(db, {
        "title": title,
        "target_amount": amt,
        "target_date": date.fromisoformat(target_date) if target_date else None,
        "note": note or None,
    })
    return RedirectResponse("/metas", status_code=303)


@router.post("/{goal_id}/progresso")
def progress_view(
    goal_id: int,
    db: Session = Depends(get_db),
    amount: str = Form(...),
):
    try:
        amt = Decimal(amount.replace(",", "."))
    except InvalidOperation as e:
        raise HTTPException(status_code=400, detail="Valor inválido") from e
    try:
        svc.add_progress(db, goal_id, amt)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return RedirectResponse("/metas", status_code=303)


@router.post("/{goal_id}/archive")
def archive_view(goal_id: int, db: Session = Depends(get_db)):
    try:
        svc.archive(db, goal_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return RedirectResponse("/metas", status_code=303)
