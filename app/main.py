from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.db import SessionLocal
from app.routers import config as config_router
from app.routers import dashboard as dashboard_router
from app.routers import fixed as fixed_router
from app.routers import goals as goals_router
from app.routers import installments as installments_router
from app.routers import reports as reports_router
from app.routers import transactions as transactions_router
from app.services.seed import seed_all

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    with SessionLocal() as db:
        seed_all(db)
    yield


app = FastAPI(title="MyFinanceApp", version="0.1.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

app.include_router(config_router.router)
app.include_router(dashboard_router.router)
app.include_router(goals_router.router)
app.include_router(transactions_router.router)
app.include_router(installments_router.router)
app.include_router(fixed_router.router)
app.include_router(reports_router.router)


@app.get("/health", response_class=HTMLResponse)
def health() -> str:
    return "<h1>ok</h1>"
