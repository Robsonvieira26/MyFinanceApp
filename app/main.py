from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="MyFinanceApp", version="0.1.0")


@app.get("/health", response_class=HTMLResponse)
def health() -> str:
    return "<h1>ok</h1>"
