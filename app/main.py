from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.db import SessionLocal
from app.services.seed import seed_all


@asynccontextmanager
async def lifespan(app: FastAPI):
    with SessionLocal() as db:
        seed_all(db)
    yield


app = FastAPI(title="MyFinanceApp", version="0.1.0", lifespan=lifespan)


@app.get("/health", response_class=HTMLResponse)
def health() -> str:
    return "<h1>ok</h1>"
