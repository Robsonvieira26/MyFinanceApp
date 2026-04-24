# MyFinanceApp — Plano de Implementação

> **Para agentes de execução:** SUB-SKILL OBRIGATÓRIA — use `superpowers:subagent-driven-development` (recomendado) ou `superpowers:executing-plans` para executar tarefa por tarefa. Passos usam checkbox `- [ ]` para rastreamento.

**Objetivo:** Construir um sistema de finanças pessoais dockerizado (Python + FastAPI + HTMX + Postgres) com dashboard mensal, ciclo de fatura de crédito, parcelados, fixos recorrentes, metas, alertas e projeção futura.

**Arquitetura:** Monólito SSR com HTMX para interações parciais. Services como funções puras separadas dos routers. Parcelas materializadas no banco; fixos projetados on-demand. Banco Postgres via volume Docker nomeado. Deploy via docker compose em servidor caseiro; atualizações por `update.sh` com backup automático.

**Stack:** Python 3.12, FastAPI, Jinja2, HTMX, SQLAlchemy 2 + Alembic, Pydantic v2, PostgreSQL 16, Chart.js (CDN), JetBrains Mono, Docker + docker compose, pytest.

**Cadência Git:** Cada tarefa concluída = 1 commit + `git push origin main` imediato. Remote: `git@github.com:Robsonvieira26/MyFinanceApp.git`.

---

## Mapa de arquivos

Estrutura final do repositório:

```
MyFinanceApp/
├── app/
│   ├── __init__.py
│   ├── main.py                      # bootstrap FastAPI
│   ├── config.py                    # Settings via env
│   ├── db.py                        # engine + SessionLocal
│   ├── deps.py                      # dependências FastAPI (get_db)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                  # Declarative base + mixins
│   │   ├── source.py
│   │   ├── category.py
│   │   ├── transaction.py
│   │   ├── installment_plan.py
│   │   ├── fixed_rule.py
│   │   ├── budget.py
│   │   ├── goal.py
│   │   └── alert.py
│   ├── schemas/                     # Pydantic v2
│   │   ├── __init__.py
│   │   ├── transaction.py
│   │   ├── installment.py
│   │   ├── fixed.py
│   │   ├── budget.py
│   │   └── goal.py
│   ├── services/                    # funções puras
│   │   ├── __init__.py
│   │   ├── fatura.py
│   │   ├── installments.py
│   │   ├── fixed_projection.py
│   │   ├── dashboard.py
│   │   ├── projection.py
│   │   ├── alerts.py
│   │   └── reports.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── dashboard.py
│   │   ├── transactions.py
│   │   ├── installments.py
│   │   ├── fixed.py
│   │   ├── reports.py
│   │   ├── projection.py
│   │   ├── goals.py
│   │   └── config.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── transactions/
│   │   ├── installments/
│   │   ├── fixed/
│   │   ├── reports/
│   │   ├── projection/
│   │   ├── goals/
│   │   ├── config/
│   │   └── _partials/
│   └── static/
│       ├── css/app.css
│       └── js/app.js
├── migrations/                      # Alembic
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── tests/
│   ├── conftest.py
│   ├── services/
│   └── routers/
├── docker/
│   ├── Dockerfile
│   └── postgres/init.sql
├── scripts/
│   ├── update.sh
│   ├── backup.sh
│   └── restore.sh
├── backups/                         # (gitignored) dumps .sql.gz
├── docker-compose.yml
├── pyproject.toml
├── alembic.ini
├── .env.example
├── .gitignore
├── .dockerignore
└── README.md
```

---

## Milestone 1 — Fundação

### Task 1.1: Inicializar repositório git e criar `.gitignore`

**Files:**
- Create: `.gitignore`

- [ ] **Step 1.1.1: `git init` no diretório do projeto**

```bash
cd /c/Users/robso/Code/Finance
git init -b main
git remote add origin git@github.com:Robsonvieira26/MyFinanceApp.git
```

- [ ] **Step 1.1.2: Criar `.gitignore`**

Arquivo: `.gitignore`

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
env/
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/
.ruff_cache/
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Env & secrets
.env
.env.local
.env.*.local

# Backups e dumps
backups/
*.sql
*.sql.gz
!docker/postgres/init.sql

# Brainstorm artefatos
.superpowers/
.claude/

# Logs
*.log
```

- [ ] **Step 1.1.3: Primeiro commit**

```bash
git add .gitignore docs/
git commit -m "chore: inicializa repositório com .gitignore e spec"
git push -u origin main
```

Expected: push para `main` no remote com sucesso.

---

### Task 1.2: `pyproject.toml` e estrutura Python base

**Files:**
- Create: `pyproject.toml`
- Create: `app/__init__.py`
- Create: `app/main.py`
- Create: `app/config.py`

- [ ] **Step 1.2.1: Criar `pyproject.toml`**

Arquivo: `pyproject.toml`

```toml
[project]
name = "myfinanceapp"
version = "0.1.0"
description = "Sistema pessoal de finanças"
requires-python = ">=3.12"
dependencies = [
  "fastapi==0.115.*",
  "uvicorn[standard]==0.32.*",
  "jinja2==3.1.*",
  "sqlalchemy==2.0.*",
  "psycopg[binary]==3.2.*",
  "alembic==1.14.*",
  "pydantic==2.10.*",
  "pydantic-settings==2.6.*",
  "python-multipart==0.0.*",
  "python-dateutil==2.9.*",
]

[project.optional-dependencies]
dev = [
  "pytest==8.3.*",
  "pytest-asyncio==0.24.*",
  "httpx==0.28.*",
  "ruff==0.8.*",
]

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B", "SIM"]
ignore = ["E501"]
```

- [ ] **Step 1.2.2: Criar `app/__init__.py` (vazio)**

Arquivo: `app/__init__.py`

```python
```

- [ ] **Step 1.2.3: Criar `app/config.py` com Settings**

Arquivo: `app/config.py`

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://finance:finance@localhost:5433/finance"
    tz: str = "America/Sao_Paulo"
    debug: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
```

- [ ] **Step 1.2.4: Criar `app/main.py` com app FastAPI mínimo**

Arquivo: `app/main.py`

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="MyFinanceApp", version="0.1.0")


@app.get("/health", response_class=HTMLResponse)
def health() -> str:
    return "<h1>ok</h1>"
```

- [ ] **Step 1.2.5: Commit e push**

```bash
git add pyproject.toml app/
git commit -m "feat: esqueleto Python com FastAPI e config via env"
git push origin main
```

---

### Task 1.3: Dockerfile e docker-compose

**Files:**
- Create: `docker/Dockerfile`
- Create: `docker/postgres/init.sql`
- Create: `docker-compose.yml`
- Create: `.env.example`
- Create: `.dockerignore`

- [ ] **Step 1.3.1: Criar `docker/Dockerfile`**

Arquivo: `docker/Dockerfile`

```dockerfile
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install -e ".[dev]"

COPY app/ ./app/
COPY migrations/ ./migrations/
COPY alembic.ini ./

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 1.3.2: Criar `docker/postgres/init.sql`**

Arquivo: `docker/postgres/init.sql`

```sql
-- Extensões úteis
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
```

- [ ] **Step 1.3.3: Criar `.dockerignore`**

Arquivo: `.dockerignore`

```
.git
.gitignore
.venv
venv
__pycache__
*.pyc
.pytest_cache
.ruff_cache
.mypy_cache
.env
.env.local
backups/
docs/
.claude/
.superpowers/
tests/
README.md
```

- [ ] **Step 1.3.4: Criar `docker-compose.yml`**

Arquivo: `docker-compose.yml`

```yaml
services:
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-finance}
      POSTGRES_USER: ${POSTGRES_USER:-finance}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?senha do postgres obrigatória}
    volumes:
      - finance_pgdata:/var/lib/postgresql/data
      - ./docker/postgres/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    ports:
      - "5433:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 5s
      timeout: 3s
      retries: 10
    networks:
      - finance_net

  web:
    build:
      context: .
      dockerfile: docker/Dockerfile
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql+psycopg://${POSTGRES_USER:-finance}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB:-finance}
      TZ: ${TZ:-America/Sao_Paulo}
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "8765:8000"
    networks:
      - finance_net

volumes:
  finance_pgdata:
    name: finance_pgdata

networks:
  finance_net:
    driver: bridge
```

- [ ] **Step 1.3.5: Criar `.env.example`**

Arquivo: `.env.example`

```bash
POSTGRES_DB=finance
POSTGRES_USER=finance
POSTGRES_PASSWORD=troque-esta-senha
TZ=America/Sao_Paulo
```

- [ ] **Step 1.3.6: Subir containers para validar**

```bash
cp .env.example .env
# edite .env e coloque uma senha real
docker compose up -d --build
curl http://localhost:8765/health
```

Expected: HTTP 200 com `<h1>ok</h1>`. Se falhar, ver `docker compose logs web`.

- [ ] **Step 1.3.7: Commit e push**

```bash
git add docker/ docker-compose.yml .env.example .dockerignore
git commit -m "infra: docker compose com web e postgres (portas 8765/5433)"
git push origin main
```

---

### Task 1.4: Conexão DB + Alembic + base SQLAlchemy

**Files:**
- Create: `app/db.py`
- Create: `app/deps.py`
- Create: `app/models/__init__.py`
- Create: `app/models/base.py`
- Create: `alembic.ini`
- Create: `migrations/env.py`
- Create: `migrations/script.py.mako`

- [ ] **Step 1.4.1: Criar `app/db.py`**

Arquivo: `app/db.py`

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
```

- [ ] **Step 1.4.2: Criar `app/deps.py`**

Arquivo: `app/deps.py`

```python
from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 1.4.3: Criar `app/models/base.py`**

Arquivo: `app/models/base.py`

```python
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
```

- [ ] **Step 1.4.4: Criar `app/models/__init__.py`**

Arquivo: `app/models/__init__.py`

```python
from app.models.base import Base

__all__ = ["Base"]
```

- [ ] **Step 1.4.5: Inicializar Alembic**

Executa dentro do container `web` para gerar a estrutura padrão:

```bash
docker compose run --rm web alembic init -t generic migrations
```

Depois, sobrescreva os arquivos gerados com os abaixo.

- [ ] **Step 1.4.6: Sobrescrever `alembic.ini`**

Arquivo: `alembic.ini`

```ini
[alembic]
script_location = migrations
sqlalchemy.url = postgresql+psycopg://finance:finance@db:5432/finance
prepend_sys_path = .
timezone = UTC

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

- [ ] **Step 1.4.7: Sobrescrever `migrations/env.py`**

Arquivo: `migrations/env.py`

```python
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.config import settings
from app.models import Base

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **Step 1.4.8: Rebuild da imagem e verificar Alembic**

```bash
docker compose build web
docker compose run --rm web alembic current
```

Expected: "Current revision(s): (empty)" (ou similar). Se der erro de conexão, verifique `.env`.

- [ ] **Step 1.4.9: Commit e push**

```bash
git add app/db.py app/deps.py app/models/ alembic.ini migrations/
git commit -m "infra: integra SQLAlchemy e Alembic com metadata do app"
git push origin main
```

---

### Task 1.5: Modelos `Source` e `Category` + seed inicial

**Files:**
- Create: `app/models/source.py`
- Create: `app/models/category.py`
- Create: `migrations/versions/0001_initial_sources_and_categories.py`
- Create: `app/services/__init__.py`
- Create: `app/services/seed.py`

- [ ] **Step 1.5.1: Criar `app/models/source.py`**

Arquivo: `app/models/source.py`

```python
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Source(Base, TimestampMixin):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    kind: Mapped[str] = mapped_column(String(16), nullable=False)  # 'hybrid' | 'debit'
    closing_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    due_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    archived: Mapped[bool] = mapped_column(default=False, nullable=False)
```

- [ ] **Step 1.5.2: Criar `app/models/category.py`**

Arquivo: `app/models/category.py`

```python
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Category(Base, TimestampMixin):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String(48), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    icon: Mapped[str | None] = mapped_column(String(8), nullable=True)
    archived: Mapped[bool] = mapped_column(default=False, nullable=False)
```

- [ ] **Step 1.5.3: Exportar modelos em `app/models/__init__.py`**

Arquivo: `app/models/__init__.py`

```python
from app.models.base import Base
from app.models.category import Category
from app.models.source import Source

__all__ = ["Base", "Category", "Source"]
```

- [ ] **Step 1.5.4: Gerar migration autogerada**

```bash
docker compose run --rm web alembic revision --autogenerate -m "initial sources and categories"
```

Renomeie o arquivo gerado em `migrations/versions/` para `0001_initial_sources_and_categories.py` e verifique que o conteúdo cria as duas tabelas.

- [ ] **Step 1.5.5: Aplicar migration**

```bash
docker compose run --rm web alembic upgrade head
```

Expected: "Running upgrade -> 0001, initial sources and categories".

- [ ] **Step 1.5.6: Criar `app/services/__init__.py` (vazio)**

Arquivo: `app/services/__init__.py`

```python
```

- [ ] **Step 1.5.7: Criar `app/services/seed.py` com fontes e categorias padrão**

Arquivo: `app/services/seed.py`

```python
from sqlalchemy.orm import Session

from app.models import Category, Source

DEFAULT_SOURCES = [
    {"slug": "conta-principal", "name": "Conta Principal", "kind": "hybrid",
     "closing_day": 4, "due_day": 10},
    {"slug": "va", "name": "VA (Alelo)", "kind": "debit", "closing_day": None, "due_day": None},
    {"slug": "vt", "name": "VT (Flash)", "kind": "debit", "closing_day": None, "due_day": None},
]

DEFAULT_CATEGORIES = [
    {"slug": "moradia", "name": "Moradia", "icon": "🏠"},
    {"slug": "mercado", "name": "Mercado", "icon": "🛒"},
    {"slug": "transporte", "name": "Transporte", "icon": "🚗"},
    {"slug": "alimentacao", "name": "Alimentação", "icon": "🍽"},
    {"slug": "lazer", "name": "Lazer", "icon": "🎮"},
    {"slug": "saude", "name": "Saúde", "icon": "⚕"},
    {"slug": "assinaturas", "name": "Assinaturas", "icon": "📺"},
    {"slug": "educacao", "name": "Educação", "icon": "📚"},
    {"slug": "outros", "name": "Outros", "icon": "•"},
]


def seed_sources(db: Session) -> None:
    for data in DEFAULT_SOURCES:
        exists = db.query(Source).filter_by(slug=data["slug"]).first()
        if not exists:
            db.add(Source(**data))
    db.commit()


def seed_categories(db: Session) -> None:
    for data in DEFAULT_CATEGORIES:
        exists = db.query(Category).filter_by(slug=data["slug"]).first()
        if not exists:
            db.add(Category(**data))
    db.commit()


def seed_all(db: Session) -> None:
    seed_sources(db)
    seed_categories(db)
```

- [ ] **Step 1.5.8: Executar seed**

Atualizar `app/main.py` para rodar seed no startup:

Arquivo: `app/main.py`

```python
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
```

- [ ] **Step 1.5.9: Rebuild + restart + validar**

```bash
docker compose up -d --build web
docker compose exec db psql -U finance -d finance -c "SELECT slug, name FROM sources;"
docker compose exec db psql -U finance -d finance -c "SELECT slug, name FROM categories;"
```

Expected: 3 fontes + 9 categorias listadas.

- [ ] **Step 1.5.10: Commit e push**

```bash
git add app/models/ app/services/ app/main.py migrations/versions/
git commit -m "feat: modelos source e category com seed inicial"
git push origin main
```

---

### Task 1.6: Base template + tema Bloomberg-roxo + static files

**Files:**
- Create: `app/templates/base.html`
- Create: `app/templates/_partials/sidebar.html`
- Create: `app/templates/_partials/topbar.html`
- Create: `app/static/css/app.css`
- Create: `app/static/js/app.js`
- Modify: `app/main.py`

- [ ] **Step 1.6.1: Atualizar `app/main.py` com static e templates**

Arquivo: `app/main.py`

```python
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.db import SessionLocal
from app.services.seed import seed_all

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    with SessionLocal() as db:
        seed_all(db)
    yield


app = FastAPI(title="MyFinanceApp", version="0.1.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/health", response_class=HTMLResponse)
def health() -> str:
    return "<h1>ok</h1>"


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "dashboard.html", {"active_nav": "dashboard", "page_title": "Dashboard"}
    )
```

- [ ] **Step 1.6.2: Criar `app/static/css/app.css` (tema completo, responsivo)**

Arquivo: `app/static/css/app.css`

```css
:root {
  --bg: #0B0E11;
  --bg-2: #0E1217;
  --bg-3: #13171D;
  --bg-4: #1A1F26;
  --border: #232830;
  --border-2: #2E3540;
  --text: #D8D4C8;
  --muted: #8B8F99;
  --dim: #5A5F6B;
  --primary: #C084FC;
  --primary-2: #A855F7;
  --primary-3: #7C3AED;
  --primary-soft: #E0C4FF;
  --primary-glow: rgba(192,132,252,0.35);
  --ok: #4AC776;
  --warn: #FF8B6B;
  --err: #FF5A5F;
  --info: #88C0D0;
  --sidebar-w: 232px;
  --header-h: 42px;
  --radius: 0;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  background: var(--bg); color: var(--text);
  font-family: "JetBrains Mono", ui-monospace, "Courier New", monospace;
  font-size: 12.5px; line-height: 1.55;
  min-height: 100vh;
}
body::before {
  content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 100;
  background: repeating-linear-gradient(to bottom, transparent 0, transparent 2px,
                                         rgba(255,255,255,0.013) 2px, rgba(255,255,255,0.013) 3px);
}
body::after {
  content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 101;
  background: radial-gradient(ellipse at 50% 45%, transparent 40%, rgba(0,0,0,0.45) 100%);
}

a { color: inherit; text-decoration: none; }

.app { display: grid; grid-template-columns: var(--sidebar-w) 1fr; min-height: 100vh; position: relative; z-index: 1; }

/* ========== SIDEBAR ========== */
.side {
  background: linear-gradient(180deg, rgba(192,132,252,0.06), transparent 40%), var(--bg);
  border-right: 1px solid var(--border);
  padding: 22px 18px;
  display: flex; flex-direction: column;
}
.brand {
  font-size: 22px; font-weight: 700; color: var(--text);
  letter-spacing: 0.02em; line-height: 1;
  text-shadow: 0 0 12px var(--primary-glow);
}
.brand .slash { color: var(--primary); text-shadow: 0 0 14px var(--primary-glow); }
.brand .v { color: var(--muted); font-weight: 400; font-size: 11px; }
.brand-sub {
  margin-top: 6px; font-size: 9.5px; letter-spacing: 0.28em;
  color: var(--muted); text-transform: uppercase;
}

.session {
  margin-top: 20px; padding: 10px 12px;
  background: var(--bg-2); border: 1px solid var(--border);
  font-size: 10.5px; color: var(--muted); letter-spacing: 0.04em;
}
.session .kv { display: flex; justify-content: space-between; padding: 2px 0; }
.session .kv .k { color: var(--dim); }
.session .kv .v { color: var(--text); font-variant-numeric: tabular-nums; }
.session .kv .v.ok { color: var(--ok); }
.session .kv .v.pu { color: var(--primary); }

.nav { margin-top: 20px; display: flex; flex-direction: column; gap: 1px; }
.nav .group { padding: 14px 4px 6px; font-size: 9px; letter-spacing: 0.32em; text-transform: uppercase; color: var(--dim); }
.nav a {
  display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 10px;
  padding: 8px 10px; color: var(--muted);
  font-size: 11.5px; letter-spacing: 0.08em; text-transform: uppercase;
  border-left: 2px solid transparent;
  transition: all 0.14s ease;
}
.nav a:hover { background: rgba(192,132,252,0.06); color: var(--text); }
.nav a .n { font-size: 9px; color: var(--dim); letter-spacing: 0.15em; font-variant-numeric: tabular-nums; }
.nav a .dot { width: 6px; height: 6px; border-radius: 50%; background: var(--dim); }
.nav a.active {
  background: rgba(192,132,252,0.1); color: var(--primary);
  border-left-color: var(--primary);
  text-shadow: 0 0 8px var(--primary-glow);
}
.nav a.active .dot { background: var(--primary); box-shadow: 0 0 8px var(--primary); }
.nav a.active .n { color: var(--primary-soft); }

.side-foot {
  margin-top: auto; padding-top: 16px; border-top: 1px solid var(--border);
  font-size: 9.5px; color: var(--dim); letter-spacing: 0.12em; text-transform: uppercase;
  line-height: 1.7;
}
.side-foot .ln { display: flex; justify-content: space-between; }
.side-foot .ln strong { color: var(--primary); font-weight: 500; }
.side-foot .ln .ok { color: var(--ok); }

/* ========== MAIN ========== */
.main { display: flex; flex-direction: column; min-width: 0; }

.topbar {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 22px; background: var(--bg-3); border-bottom: 1px solid var(--border);
}
.topbar .crumbs { font-size: 10px; color: var(--muted); letter-spacing: 0.18em; text-transform: uppercase; }
.topbar .crumbs strong { color: var(--primary); font-weight: 500; }
.topbar .crumbs .sep { color: var(--dim); margin: 0 8px; }
.topbar .status { font-size: 10px; color: var(--muted); letter-spacing: 0.06em; display: flex; gap: 16px; align-items: center; }
.topbar .status .ok { color: var(--ok); }
.topbar .status .pulse {
  width: 6px; height: 6px; border-radius: 50%; background: var(--ok);
  box-shadow: 0 0 8px var(--ok); animation: pulse 1.6s steps(3) infinite;
  display: inline-block; margin-right: 6px; vertical-align: 1px;
}
@keyframes pulse { 0%, 60% { opacity: 1; } 61%, 100% { opacity: 0.3; } }

.header {
  padding: 20px 24px 16px; display: flex; justify-content: space-between; align-items: flex-end;
  border-bottom: 1px solid var(--border);
}
.header h1 { font-size: 28px; font-weight: 500; color: var(--text); letter-spacing: -0.01em; line-height: 1; }
.header h1 .blink { display: inline-block; color: var(--primary); margin-left: 10px; animation: blink 1.1s steps(2) infinite; font-weight: 400; }
@keyframes blink { 0%, 50% { opacity: 1; } 51%, 100% { opacity: 0; } }
.header .subtitle { margin-top: 6px; font-size: 11px; color: var(--muted); letter-spacing: 0.1em; }
.header .actions { display: flex; gap: 8px; flex-wrap: wrap; }
.btn {
  padding: 8px 14px; background: transparent; color: var(--primary);
  border: 1px solid var(--primary); font-family: inherit; font-size: 10.5px;
  letter-spacing: 0.2em; text-transform: uppercase; cursor: pointer;
  transition: all 0.15s;
}
.btn:hover { background: var(--primary); color: var(--bg); box-shadow: 0 0 18px var(--primary-glow); }
.btn.secondary { color: var(--muted); border-color: var(--border-2); }
.btn.secondary:hover { color: var(--text); border-color: var(--muted); background: transparent; box-shadow: none; }
.btn.danger { color: var(--err); border-color: var(--err); }
.btn.danger:hover { background: var(--err); color: var(--bg); box-shadow: 0 0 18px rgba(255,90,95,0.4); }

.content { padding: 18px 22px; flex: 1; display: flex; flex-direction: column; gap: 14px; }

/* Menu hamburger (mobile) */
.hamburger {
  display: none; width: 40px; height: 40px; border: 1px solid var(--border-2);
  background: transparent; color: var(--primary); cursor: pointer;
  font-size: 18px; line-height: 1;
}
.side-backdrop {
  display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.7);
  z-index: 50; backdrop-filter: blur(4px);
}

/* ========== RESPONSIVE ========== */
@media (max-width: 1199px) {
  :root { --sidebar-w: 200px; }
  .content { padding: 14px 16px; }
  .header { padding: 16px 16px 12px; }
  .header h1 { font-size: 22px; }
  .topbar { padding: 10px 16px; }
}
@media (max-width: 767px) {
  .app { grid-template-columns: 1fr; }
  .side {
    position: fixed; left: 0; top: 0; bottom: 0; width: 260px;
    z-index: 60; transform: translateX(-100%); transition: transform 0.2s ease;
  }
  body.side-open .side { transform: translateX(0); }
  body.side-open .side-backdrop { display: block; }
  .hamburger { display: block; }
  .topbar { padding: 8px 12px; }
  .header { flex-direction: column; align-items: stretch; gap: 12px; padding: 14px 12px; }
  .header h1 { font-size: 20px; }
  .header .actions { justify-content: flex-start; }
  .content { padding: 12px; }
  body { font-size: 12px; }
}
```

- [ ] **Step 1.6.3: Criar `app/static/js/app.js`**

Arquivo: `app/static/js/app.js`

```javascript
// Menu hamburger em mobile
document.addEventListener("DOMContentLoaded", () => {
  const btn = document.querySelector(".hamburger");
  const backdrop = document.querySelector(".side-backdrop");
  if (btn) {
    btn.addEventListener("click", () => document.body.classList.toggle("side-open"));
  }
  if (backdrop) {
    backdrop.addEventListener("click", () => document.body.classList.remove("side-open"));
  }
});
```

- [ ] **Step 1.6.4: Criar `app/templates/_partials/sidebar.html`**

Arquivo: `app/templates/_partials/sidebar.html`

```html
<aside class="side">
  <div class="brand">FIN<span class="slash">//</span>26<br><span class="v">v0.1.0</span></div>
  <div class="brand-sub">finance-term · sessão local</div>

  <div class="session">
    <div class="kv"><span class="k">DB</span><span class="v pu">fin_db:5433</span></div>
    <div class="kv"><span class="k">status</span><span class="v ok">● online</span></div>
  </div>

  <nav class="nav">
    <div class="group">— navegação</div>
    <a href="/" class="{% if active_nav == 'dashboard' %}active{% endif %}"><span class="dot"></span><span>Dashboard</span><span class="n">01</span></a>
    <a href="/lancamentos" class="{% if active_nav == 'transactions' %}active{% endif %}"><span class="dot"></span><span>Lançamentos</span><span class="n">02</span></a>
    <a href="/parcelados" class="{% if active_nav == 'installments' %}active{% endif %}"><span class="dot"></span><span>Parcelados</span><span class="n">03</span></a>
    <a href="/fixos" class="{% if active_nav == 'fixed' %}active{% endif %}"><span class="dot"></span><span>Fixos</span><span class="n">04</span></a>
    <a href="/relatorios" class="{% if active_nav == 'reports' %}active{% endif %}"><span class="dot"></span><span>Relatórios</span><span class="n">05</span></a>
    <a href="/projecao" class="{% if active_nav == 'projection' %}active{% endif %}"><span class="dot"></span><span>Projeção</span><span class="n">06</span></a>
    <a href="/metas" class="{% if active_nav == 'goals' %}active{% endif %}"><span class="dot"></span><span>Metas</span><span class="n">07</span></a>

    <div class="group">— config</div>
    <a href="/config/categorias" class="{% if active_nav == 'categories' %}active{% endif %}"><span class="dot"></span><span>Categorias</span><span class="n">08</span></a>
    <a href="/config/fontes" class="{% if active_nav == 'sources' %}active{% endif %}"><span class="dot"></span><span>Fontes</span><span class="n">09</span></a>
    <a href="/config/sistema" class="{% if active_nav == 'system' %}active{% endif %}"><span class="dot"></span><span>Sistema</span><span class="n">10</span></a>
  </nav>

  <div class="side-foot">
    <div class="ln"><span>exerc</span><strong>2026</strong></div>
    <div class="ln"><span>moeda</span><strong>BRL</strong></div>
    <div class="ln"><span>sync</span><span class="ok">● live</span></div>
  </div>
</aside>
```

- [ ] **Step 1.6.5: Criar `app/templates/_partials/topbar.html`**

Arquivo: `app/templates/_partials/topbar.html`

```html
<div class="topbar">
  <div style="display:flex; align-items:center; gap:12px;">
    <button class="hamburger" aria-label="menu">≡</button>
    <div class="crumbs">~/ <span class="sep">·</span> <strong>{{ page_title or "—" }}</strong></div>
  </div>
  <div class="status">
    <span><span class="pulse"></span>online</span>
    <span>db <span class="ok">ok</span></span>
  </div>
</div>
```

- [ ] **Step 1.6.6: Criar `app/templates/base.html`**

Arquivo: `app/templates/base.html`

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ page_title }} — MyFinanceApp</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/static/css/app.css">
<script src="https://unpkg.com/htmx.org@2.0.3"></script>
</head>
<body>
<div class="side-backdrop"></div>
<div class="app">
  {% include "_partials/sidebar.html" %}
  <main class="main">
    {% include "_partials/topbar.html" %}
    {% block content %}{% endblock %}
  </main>
</div>
<script src="/static/js/app.js"></script>
{% block scripts %}{% endblock %}
</body>
</html>
```

- [ ] **Step 1.6.7: Criar placeholder `app/templates/dashboard.html`**

Arquivo: `app/templates/dashboard.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="header">
  <div>
    <h1>Dashboard<span class="blink">▊</span></h1>
    <div class="subtitle">em construção · v0.1</div>
  </div>
</div>
<div class="content">
  <p style="color: var(--muted);">Dashboard será implementado no Milestone 4.</p>
</div>
{% endblock %}
```

- [ ] **Step 1.6.8: Rebuild + validar**

```bash
docker compose up -d --build web
# abra http://localhost:8765 no navegador
```

Expected: layout completo com sidebar roxa, topbar e placeholder "em construção". Redimensione a janela até < 768px para ver o menu hamburger.

- [ ] **Step 1.6.9: Commit e push**

```bash
git add app/main.py app/static/ app/templates/
git commit -m "feat: base template com tema Bloomberg-roxo e responsividade"
git push origin main
```

---

### Task 1.7: README inicial

**Files:**
- Create: `README.md`

- [ ] **Step 1.7.1: Criar `README.md`**

Arquivo: `README.md`

````markdown
# MyFinanceApp

Sistema pessoal de finanças — dashboard mensal com ciclo de fatura de cartão de crédito, gastos fixos recorrentes, parcelamentos, metas e projeções futuras. Executa em Docker no servidor caseiro.

Projeto monousuário, sem login, desenhado para uso em rede local.

## Stack

- Python 3.12 + FastAPI + HTMX + Jinja2
- SQLAlchemy 2 + Alembic
- PostgreSQL 16
- Chart.js (via CDN)
- Docker + docker compose

## Pré-requisitos

- Docker e docker compose instalados.
- Git.

## Primeira execução

```bash
git clone git@github.com:Robsonvieira26/MyFinanceApp.git
cd MyFinanceApp
cp .env.example .env
# edite .env e defina POSTGRES_PASSWORD
docker compose up -d --build
```

Aplique as migrations e rode o seed inicial:

```bash
docker compose exec web alembic upgrade head
```

Acesse em `http://<host>:8765`.

## Portas

| Serviço    | Host | Container |
|------------|------|-----------|
| Web        | 8765 | 8000      |
| PostgreSQL | 5433 | 5432      |

## Atualização (produção)

```bash
./scripts/update.sh
```

O script faz backup automático do banco antes de atualizar (`git pull` + rebuild + migrations).

## Backup manual

```bash
./scripts/backup.sh
```

Salva dump em `backups/finance_YYYY-MM-DD_HHMMSS.sql.gz`. Mantém os últimos 14 backups.

## Restauração

```bash
./scripts/restore.sh backups/finance_2026-04-23_193000.sql.gz
```

Pede confirmação explícita antes de apagar dados.

## Estrutura

```
app/         # código do servidor FastAPI
  models/    # SQLAlchemy
  schemas/   # Pydantic
  services/  # regras de negócio puras
  routers/   # endpoints HTTP
  templates/ # Jinja2
  static/    # CSS + JS
migrations/  # Alembic
tests/
scripts/     # update/backup/restore
docker/      # Dockerfile e init.sql
```

## Contribuição

Projeto pessoal. Não aceita PRs externos.
````

- [ ] **Step 1.7.2: Commit e push**

```bash
git add README.md
git commit -m "docs: README com instruções de deploy, backup e restore"
git push origin main
```

---

### Task 1.8: Pytest + fixture de DB em memória

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `tests/test_smoke.py`

- [ ] **Step 1.8.1: Criar `tests/__init__.py` (vazio)**

Arquivo: `tests/__init__.py`

```python
```

- [ ] **Step 1.8.2: Criar `tests/conftest.py`**

Arquivo: `tests/conftest.py`

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.models import Base


@pytest.fixture
def engine():
    eng = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def db(engine) -> Session:
    SessionTest = sessionmaker(bind=engine, future=True)
    with SessionTest() as session:
        yield session
```

- [ ] **Step 1.8.3: Criar `tests/test_smoke.py`**

Arquivo: `tests/test_smoke.py`

```python
from app.models import Category, Source
from app.services.seed import seed_all


def test_seed_creates_three_sources(db):
    seed_all(db)
    sources = db.query(Source).all()
    slugs = {s.slug for s in sources}
    assert slugs == {"conta-principal", "va", "vt"}


def test_seed_creates_nine_categories(db):
    seed_all(db)
    assert db.query(Category).count() == 9


def test_seed_is_idempotent(db):
    seed_all(db)
    seed_all(db)
    assert db.query(Source).count() == 3
    assert db.query(Category).count() == 9
```

- [ ] **Step 1.8.4: Rodar os testes**

```bash
docker compose run --rm web pytest tests/test_smoke.py -v
```

Expected: 3 testes PASS.

- [ ] **Step 1.8.5: Commit e push**

```bash
git add tests/
git commit -m "test: fixtures de DB em memória e smoke test do seed"
git push origin main
```

---

**Marco M1 alcançado:** projeto inicializado, containers subindo, tema visual funcional, migration/seed operacionais, testes rodando, README publicado. Continua em M2.

---

## Milestone 2 — Lançamentos básicos (CRUD)

### Task 2.1: Modelo `Transaction` e migration

**Files:**
- Create: `app/models/transaction.py`
- Modify: `app/models/__init__.py`
- Create: `migrations/versions/0002_transactions.py`

- [ ] **Step 2.1.1: Criar `app/models/transaction.py`**

Arquivo: `app/models/transaction.py`

```python
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)

    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    payment_mode: Mapped[str] = mapped_column(String(16), nullable=False)  # credit|debit|pix
    type: Mapped[str] = mapped_column(String(16), nullable=False, default="expense")  # expense|income
    origin: Mapped[str] = mapped_column(String(16), nullable=False, default="manual")  # manual|installment|fixed
    origin_ref_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    status: Mapped[str] = mapped_column(String(16), nullable=False, default="confirmed")  # confirmed|projected
    actual_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    actual_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    source = relationship("Source")
    category = relationship("Category")
```

- [ ] **Step 2.1.2: Atualizar `app/models/__init__.py`**

Arquivo: `app/models/__init__.py`

```python
from app.models.base import Base
from app.models.category import Category
from app.models.source import Source
from app.models.transaction import Transaction

__all__ = ["Base", "Category", "Source", "Transaction"]
```

- [ ] **Step 2.1.3: Gerar migration**

```bash
docker compose run --rm web alembic revision --autogenerate -m "transactions"
```

Renomear o arquivo para `migrations/versions/0002_transactions.py` e conferir que cria a tabela `transactions` com as colunas do modelo.

- [ ] **Step 2.1.4: Aplicar migration**

```bash
docker compose run --rm web alembic upgrade head
```

- [ ] **Step 2.1.5: Commit e push**

```bash
git add app/models/transaction.py app/models/__init__.py migrations/versions/0002_transactions.py
git commit -m "feat: modelo Transaction com amount, data, fonte, categoria, modo"
git push origin main
```

---

### Task 2.2: Schemas Pydantic para Transaction

**Files:**
- Create: `app/schemas/__init__.py`
- Create: `app/schemas/transaction.py`

- [ ] **Step 2.2.1: Criar `app/schemas/__init__.py` (vazio)**

Arquivo: `app/schemas/__init__.py`

```python
```

- [ ] **Step 2.2.2: Criar `app/schemas/transaction.py`**

Arquivo: `app/schemas/transaction.py`

```python
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TransactionBase(BaseModel):
    description: str = Field(min_length=1, max_length=200)
    amount: Decimal = Field(gt=0, decimal_places=2)
    date: date
    source_id: int
    category_id: int
    payment_mode: Literal["credit", "debit", "pix"]
    type: Literal["expense", "income"] = "expense"
    note: str | None = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    description: str | None = Field(default=None, min_length=1, max_length=200)
    amount: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    date: date | None = None
    source_id: int | None = None
    category_id: int | None = None
    payment_mode: Literal["credit", "debit", "pix"] | None = None
    type: Literal["expense", "income"] | None = None
    note: str | None = None


class TransactionOut(TransactionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    origin: Literal["manual", "installment", "fixed"]
    status: Literal["confirmed", "projected"]
```

- [ ] **Step 2.2.3: Commit e push**

```bash
git add app/schemas/
git commit -m "feat: schemas Pydantic de Transaction (create, update, out)"
git push origin main
```

---

### Task 2.3: Service de transactions (TDD)

**Files:**
- Create: `app/services/transactions.py`
- Create: `tests/services/__init__.py`
- Create: `tests/services/test_transactions_service.py`

- [ ] **Step 2.3.1: Criar `tests/services/__init__.py` (vazio)**

Arquivo: `tests/services/__init__.py`

```python
```

- [ ] **Step 2.3.2: Escrever os testes primeiro (vão falhar)**

Arquivo: `tests/services/test_transactions_service.py`

```python
from datetime import date
from decimal import Decimal

import pytest

from app.services import transactions as svc
from app.services.seed import seed_all


@pytest.fixture
def seeded(db):
    seed_all(db)
    return db


def _tx_data(**overrides):
    base = {
        "description": "Mercado mensal",
        "amount": Decimal("123.45"),
        "date": date(2026, 4, 10),
        "source_id": 1,
        "category_id": 2,
        "payment_mode": "debit",
        "type": "expense",
        "note": None,
    }
    base.update(overrides)
    return base


def test_create_transaction_returns_persisted_row(seeded):
    tx = svc.create(seeded, _tx_data())
    assert tx.id is not None
    assert tx.description == "Mercado mensal"
    assert tx.amount == Decimal("123.45")
    assert tx.origin == "manual"
    assert tx.status == "confirmed"


def test_list_returns_empty_initially(seeded):
    assert svc.list_all(seeded) == []


def test_list_returns_in_descending_date(seeded):
    svc.create(seeded, _tx_data(date=date(2026, 4, 1), description="A"))
    svc.create(seeded, _tx_data(date=date(2026, 4, 10), description="B"))
    svc.create(seeded, _tx_data(date=date(2026, 4, 5), description="C"))
    results = svc.list_all(seeded)
    assert [t.description for t in results] == ["B", "C", "A"]


def test_filter_by_month(seeded):
    svc.create(seeded, _tx_data(date=date(2026, 3, 30), description="mar"))
    svc.create(seeded, _tx_data(date=date(2026, 4, 2), description="abr-1"))
    svc.create(seeded, _tx_data(date=date(2026, 4, 25), description="abr-2"))
    results = svc.list_all(seeded, year=2026, month=4)
    assert {t.description for t in results} == {"abr-1", "abr-2"}


def test_filter_by_source(seeded):
    svc.create(seeded, _tx_data(source_id=1, description="principal"))
    svc.create(seeded, _tx_data(source_id=2, description="va"))
    results = svc.list_all(seeded, source_id=2)
    assert [t.description for t in results] == ["va"]


def test_filter_by_category(seeded):
    svc.create(seeded, _tx_data(category_id=1, description="moradia"))
    svc.create(seeded, _tx_data(category_id=5, description="lazer"))
    results = svc.list_all(seeded, category_id=5)
    assert [t.description for t in results] == ["lazer"]


def test_filter_by_text_matches_description_icase(seeded):
    svc.create(seeded, _tx_data(description="Uber Centro"))
    svc.create(seeded, _tx_data(description="Padaria"))
    results = svc.list_all(seeded, text="uber")
    assert [t.description for t in results] == ["Uber Centro"]


def test_update_changes_fields(seeded):
    tx = svc.create(seeded, _tx_data(description="old"))
    updated = svc.update(seeded, tx.id, {"description": "new", "amount": Decimal("999.99")})
    assert updated.description == "new"
    assert updated.amount == Decimal("999.99")


def test_update_unknown_id_raises(seeded):
    with pytest.raises(LookupError):
        svc.update(seeded, 9999, {"description": "x"})


def test_delete_removes_row(seeded):
    tx = svc.create(seeded, _tx_data())
    svc.delete(seeded, tx.id)
    assert svc.list_all(seeded) == []


def test_delete_unknown_id_raises(seeded):
    with pytest.raises(LookupError):
        svc.delete(seeded, 9999)
```

- [ ] **Step 2.3.3: Rodar testes para confirmar que falham**

```bash
docker compose run --rm web pytest tests/services/test_transactions_service.py -v
```

Expected: todos falham com "ModuleNotFoundError: No module named 'app.services.transactions'".

- [ ] **Step 2.3.4: Implementar o service**

Arquivo: `app/services/transactions.py`

```python
from calendar import monthrange
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Transaction


def create(db: Session, data: dict[str, Any]) -> Transaction:
    tx = Transaction(
        origin=data.pop("origin", "manual"),
        status=data.pop("status", "confirmed"),
        **data,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


def list_all(
    db: Session,
    *,
    year: int | None = None,
    month: int | None = None,
    source_id: int | None = None,
    category_id: int | None = None,
    text: str | None = None,
    limit: int | None = None,
) -> list[Transaction]:
    stmt = select(Transaction)
    if year is not None and month is not None:
        start = date(year, month, 1)
        end_day = monthrange(year, month)[1]
        end = date(year, month, end_day)
        stmt = stmt.where(Transaction.date >= start, Transaction.date <= end)
    if source_id is not None:
        stmt = stmt.where(Transaction.source_id == source_id)
    if category_id is not None:
        stmt = stmt.where(Transaction.category_id == category_id)
    if text:
        stmt = stmt.where(Transaction.description.ilike(f"%{text}%"))
    stmt = stmt.order_by(Transaction.date.desc(), Transaction.id.desc())
    if limit is not None:
        stmt = stmt.limit(limit)
    return list(db.execute(stmt).scalars().all())


def get(db: Session, tx_id: int) -> Transaction:
    tx = db.get(Transaction, tx_id)
    if tx is None:
        raise LookupError(f"Transaction {tx_id} not found")
    return tx


def update(db: Session, tx_id: int, data: dict[str, Any]) -> Transaction:
    tx = get(db, tx_id)
    for key, value in data.items():
        if value is None:
            continue
        setattr(tx, key, value)
    db.commit()
    db.refresh(tx)
    return tx


def delete(db: Session, tx_id: int) -> None:
    tx = get(db, tx_id)
    db.delete(tx)
    db.commit()
```

- [ ] **Step 2.3.5: Rodar testes novamente**

```bash
docker compose run --rm web pytest tests/services/test_transactions_service.py -v
```

Expected: 11 testes PASS.

- [ ] **Step 2.3.6: Commit e push**

```bash
git add app/services/transactions.py tests/services/
git commit -m "feat: service de Transaction com CRUD e filtros testados"
git push origin main
```

---

### Task 2.4: Router `/lancamentos` com lista e filtros

**Files:**
- Create: `app/routers/__init__.py`
- Create: `app/routers/transactions.py`
- Create: `app/templates/transactions/list.html`
- Create: `app/templates/transactions/_row.html`
- Modify: `app/main.py`

- [ ] **Step 2.4.1: Criar `app/routers/__init__.py` (vazio)**

Arquivo: `app/routers/__init__.py`

```python
```

- [ ] **Step 2.4.2: Criar `app/routers/transactions.py`**

Arquivo: `app/routers/transactions.py`

```python
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
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
        source_id=source_id, category_id=category_id, text=text,
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


@router.post("/new")
def create_view(
    db: Session = Depends(get_db),
    description: str = ...,
    amount: str = ...,
    date_: str = ...,
    source_id: int = ...,
    category_id: int = ...,
    payment_mode: str = ...,
    type: str = "expense",
    note: str = "",
):
    from decimal import Decimal
    svc.create(db, {
        "description": description,
        "amount": Decimal(amount),
        "date": date.fromisoformat(date_),
        "source_id": source_id,
        "category_id": category_id,
        "payment_mode": payment_mode,
        "type": type,
        "note": note or None,
    })
    return RedirectResponse("/lancamentos", status_code=303)


@router.post("/{tx_id}/delete")
def delete_view(tx_id: int, db: Session = Depends(get_db)):
    try:
        svc.delete(db, tx_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return RedirectResponse("/lancamentos", status_code=303)
```

Nota: o `...` como default em FastAPI significa "obrigatório". Para receber via form submit será refinado na próxima task; por ora aceita query params.

- [ ] **Step 2.4.3: Criar template `app/templates/transactions/list.html`**

Arquivo: `app/templates/transactions/list.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="header">
  <div>
    <h1>Lançamentos<span class="blink">▊</span></h1>
    <div class="subtitle">{{ filters.month | string | rjust(2, '0') }}/{{ filters.year }} · {{ items | length }} registro(s)</div>
  </div>
  <div class="actions">
    <a class="btn" href="/lancamentos/novo">[ + ] adicionar</a>
  </div>
</div>

<div class="content">
  <form method="get" action="/lancamentos" class="filter-form">
    <div class="filters">
      <label>Mês
        <select name="month">
          {% for m in range(1, 13) %}
            <option value="{{ m }}" {% if m == filters.month %}selected{% endif %}>{{ "%02d" | format(m) }}</option>
          {% endfor %}
        </select>
      </label>
      <label>Ano
        <input type="number" name="year" value="{{ filters.year }}" min="2000" max="2100">
      </label>
      <label>Fonte
        <select name="source_id">
          <option value="">todas</option>
          {% for s in sources %}
            <option value="{{ s.id }}" {% if s.id == filters.source_id %}selected{% endif %}>{{ s.name }}</option>
          {% endfor %}
        </select>
      </label>
      <label>Categoria
        <select name="category_id">
          <option value="">todas</option>
          {% for c in categories %}
            <option value="{{ c.id }}" {% if c.id == filters.category_id %}selected{% endif %}>{{ c.name }}</option>
          {% endfor %}
        </select>
      </label>
      <label>Texto
        <input type="text" name="text" value="{{ filters.text or '' }}" placeholder="descrição...">
      </label>
      <button type="submit" class="btn secondary">filtrar</button>
    </div>
  </form>

  <table class="tx-table">
    <thead>
      <tr><th>Data</th><th>Descrição</th><th>Categoria</th><th>Fonte</th><th>Modo</th><th>Valor</th><th></th></tr>
    </thead>
    <tbody>
      {% for tx in items %}
        {% include "transactions/_row.html" %}
      {% else %}
        <tr><td colspan="7" class="empty">Sem lançamentos neste filtro.</td></tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% endblock %}
```

- [ ] **Step 2.4.4: Criar partial `app/templates/transactions/_row.html`**

Arquivo: `app/templates/transactions/_row.html`

```html
<tr>
  <td>{{ tx.date.strftime("%d/%m") }}</td>
  <td>{{ tx.description }}</td>
  <td>{{ tx.category.name }}</td>
  <td>{{ tx.source.name }}</td>
  <td><span class="pill mode-{{ tx.payment_mode }}">{{ tx.payment_mode }}</span></td>
  <td class="num">R$ {{ "%.2f" | format(tx.amount) | replace(".", ",") }}</td>
  <td>
    <form method="post" action="/lancamentos/{{ tx.id }}/delete" onsubmit="return confirm('Apagar este lançamento?')">
      <button type="submit" class="btn danger" style="padding:4px 8px; font-size:9px;">×</button>
    </form>
  </td>
</tr>
```

- [ ] **Step 2.4.5: Adicionar CSS para a tabela e formulário de filtros**

Anexar ao final de `app/static/css/app.css`:

```css
/* ========== LANÇAMENTOS ========== */
.filters { display: flex; gap: 10px; flex-wrap: wrap; align-items: flex-end; padding: 12px; background: var(--bg-2); border: 1px solid var(--border); margin-bottom: 14px; }
.filters label { display: flex; flex-direction: column; gap: 4px; font-size: 10px; color: var(--muted); letter-spacing: 0.15em; text-transform: uppercase; }
.filters input, .filters select {
  background: var(--bg); color: var(--text); border: 1px solid var(--border-2);
  font-family: inherit; font-size: 12px; padding: 6px 8px; min-width: 120px;
}
.filters input:focus, .filters select:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 8px var(--primary-glow); }

.tx-table { width: 100%; border-collapse: collapse; background: var(--bg-2); border: 1px solid var(--border); }
.tx-table th, .tx-table td { padding: 10px 14px; text-align: left; border-bottom: 1px dashed rgba(255,255,255,0.05); }
.tx-table th { background: var(--bg-3); font-size: 10px; letter-spacing: 0.22em; text-transform: uppercase; color: var(--muted); font-weight: 500; }
.tx-table td.num { text-align: right; font-variant-numeric: tabular-nums; color: var(--primary); font-weight: 500; }
.tx-table td.empty { text-align: center; padding: 32px; color: var(--dim); }
.tx-table tbody tr:hover { background: rgba(192,132,252,0.04); }

.pill { display: inline-block; padding: 2px 8px; border: 1px solid var(--border-2); font-size: 9px; letter-spacing: 0.2em; text-transform: uppercase; color: var(--muted); }
.pill.mode-credit { color: var(--primary); border-color: var(--primary); }
.pill.mode-debit { color: var(--info); border-color: var(--info); }
.pill.mode-pix { color: var(--ok); border-color: var(--ok); }

@media (max-width: 767px) {
  .tx-table thead { display: none; }
  .tx-table, .tx-table tbody, .tx-table tr, .tx-table td { display: block; }
  .tx-table tr { margin-bottom: 10px; border: 1px solid var(--border); padding: 8px; }
  .tx-table td { border: none; padding: 4px 0; }
  .tx-table td::before { content: attr(data-label); color: var(--muted); font-size: 9px; letter-spacing: 0.2em; text-transform: uppercase; margin-right: 8px; }
  .filters { flex-direction: column; align-items: stretch; }
  .filters label { width: 100%; }
  .filters input, .filters select { width: 100%; }
}
```

- [ ] **Step 2.4.6: Registrar router em `app/main.py`**

Modificar `app/main.py` adicionando a importação e `app.include_router` logo após o `app = FastAPI(...)`:

```python
from app.routers import transactions as transactions_router

# ... depois da criação do app:
app.include_router(transactions_router.router)
```

O arquivo completo fica:

```python
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.db import SessionLocal
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
app.include_router(transactions_router.router)

templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/health", response_class=HTMLResponse)
def health() -> str:
    return "<h1>ok</h1>"


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "dashboard.html", {"active_nav": "dashboard", "page_title": "Dashboard"}
    )
```

- [ ] **Step 2.4.7: Rebuild + validar no navegador**

```bash
docker compose up -d --build web
# abra http://localhost:8765/lancamentos
```

Expected: página de lançamentos aparece com filtros e tabela vazia ("Sem lançamentos neste filtro.").

- [ ] **Step 2.4.8: Commit e push**

```bash
git add app/routers/ app/templates/transactions/ app/static/css/app.css app/main.py
git commit -m "feat: página de lançamentos com filtros, lista e exclusão"
git push origin main
```

---

### Task 2.5: Formulário de criação de lançamento

**Files:**
- Create: `app/templates/transactions/new.html`
- Modify: `app/routers/transactions.py`

- [ ] **Step 2.5.1: Adicionar rota GET `/novo` no router**

Substituir `app/routers/transactions.py` por:

```python
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


@router.post("/{tx_id}/delete")
def delete_view(tx_id: int, db: Session = Depends(get_db)):
    try:
        svc.delete(db, tx_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return RedirectResponse("/lancamentos", status_code=303)
```

- [ ] **Step 2.5.2: Criar `app/templates/transactions/new.html`**

Arquivo: `app/templates/transactions/new.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="header">
  <div>
    <h1>Novo lançamento<span class="blink">▊</span></h1>
    <div class="subtitle">registre um gasto ou recebimento avulso</div>
  </div>
  <div class="actions">
    <a class="btn secondary" href="/lancamentos">[ ← ] voltar</a>
  </div>
</div>

<div class="content">
  <form method="post" action="/lancamentos/novo" class="form-card">
    <div class="form-row">
      <label>Tipo
        <select name="type">
          <option value="expense" selected>gasto</option>
          <option value="income">receita</option>
        </select>
      </label>
      <label>Data
        <input type="date" name="date" value="{{ today }}" required>
      </label>
      <label>Valor (R$)
        <input type="text" name="amount" placeholder="0,00" required pattern="[0-9]+([,.][0-9]{1,2})?">
      </label>
    </div>
    <div class="form-row">
      <label style="flex:1;">Descrição
        <input type="text" name="description" maxlength="200" required autofocus>
      </label>
    </div>
    <div class="form-row">
      <label>Fonte
        <select name="source_id" required>
          {% for s in sources %}
            <option value="{{ s.id }}">{{ s.name }}</option>
          {% endfor %}
        </select>
      </label>
      <label>Modo
        <select name="payment_mode" required>
          <option value="debit">débito</option>
          <option value="credit">crédito</option>
          <option value="pix">PIX</option>
        </select>
      </label>
      <label>Categoria
        <select name="category_id" required>
          {% for c in categories %}
            <option value="{{ c.id }}">{{ c.name }}</option>
          {% endfor %}
        </select>
      </label>
    </div>
    <div class="form-row">
      <label style="flex:1;">Nota (opcional)
        <textarea name="note" rows="2" maxlength="500"></textarea>
      </label>
    </div>
    <div class="form-actions">
      <button type="submit" class="btn">[ salvar ]</button>
    </div>
  </form>
</div>
{% endblock %}
```

- [ ] **Step 2.5.3: CSS do formulário**

Anexar ao final de `app/static/css/app.css`:

```css
/* ========== FORMULÁRIOS ========== */
.form-card { max-width: 720px; padding: 20px; background: var(--bg-2); border: 1px solid var(--border); }
.form-row { display: flex; gap: 14px; margin-bottom: 14px; flex-wrap: wrap; }
.form-row label { display: flex; flex-direction: column; gap: 6px; font-size: 10px; color: var(--muted); letter-spacing: 0.18em; text-transform: uppercase; min-width: 160px; }
.form-row input, .form-row select, .form-row textarea {
  background: var(--bg); color: var(--text); border: 1px solid var(--border-2);
  font-family: inherit; font-size: 13px; padding: 8px 10px;
}
.form-row input:focus, .form-row select:focus, .form-row textarea:focus {
  outline: none; border-color: var(--primary); box-shadow: 0 0 8px var(--primary-glow);
}
.form-actions { margin-top: 8px; display: flex; gap: 10px; }

@media (max-width: 767px) {
  .form-row { flex-direction: column; gap: 10px; }
  .form-row label { min-width: 0; }
}
```

- [ ] **Step 2.5.4: Rebuild + testar criação via navegador**

```bash
docker compose up -d --build web
# abra http://localhost:8765/lancamentos/novo
# preencha e envie; volte à lista para conferir
```

Expected: lançamento aparece na lista após o submit.

- [ ] **Step 2.5.5: Commit e push**

```bash
git add app/routers/transactions.py app/templates/transactions/new.html app/static/css/app.css
git commit -m "feat: formulário de criação de lançamento com validação de valor"
git push origin main
```

---

### Task 2.6: Edição de lançamento existente

**Files:**
- Create: `app/templates/transactions/edit.html`
- Modify: `app/routers/transactions.py`

- [ ] **Step 2.6.1: Adicionar rotas GET/POST `/lancamentos/{id}/editar`**

Adicionar em `app/routers/transactions.py` após `delete_view`:

```python
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
```

- [ ] **Step 2.6.2: Criar template `app/templates/transactions/edit.html`**

Arquivo: `app/templates/transactions/edit.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="header">
  <div>
    <h1>Editar lançamento<span class="blink">▊</span></h1>
    <div class="subtitle">id #{{ tx.id }} · origem {{ tx.origin }}</div>
  </div>
  <div class="actions">
    <a class="btn secondary" href="/lancamentos">[ ← ] voltar</a>
  </div>
</div>

<div class="content">
  <form method="post" action="/lancamentos/{{ tx.id }}/editar" class="form-card">
    <div class="form-row">
      <label>Tipo
        <select name="type">
          <option value="expense" {% if tx.type == 'expense' %}selected{% endif %}>gasto</option>
          <option value="income" {% if tx.type == 'income' %}selected{% endif %}>receita</option>
        </select>
      </label>
      <label>Data
        <input type="date" name="date" value="{{ tx.date.isoformat() }}" required>
      </label>
      <label>Valor (R$)
        <input type="text" name="amount" value="{{ '%.2f' | format(tx.amount) }}" required>
      </label>
    </div>
    <div class="form-row">
      <label style="flex:1;">Descrição
        <input type="text" name="description" value="{{ tx.description }}" maxlength="200" required>
      </label>
    </div>
    <div class="form-row">
      <label>Fonte
        <select name="source_id" required>
          {% for s in sources %}
            <option value="{{ s.id }}" {% if s.id == tx.source_id %}selected{% endif %}>{{ s.name }}</option>
          {% endfor %}
        </select>
      </label>
      <label>Modo
        <select name="payment_mode" required>
          <option value="debit" {% if tx.payment_mode == 'debit' %}selected{% endif %}>débito</option>
          <option value="credit" {% if tx.payment_mode == 'credit' %}selected{% endif %}>crédito</option>
          <option value="pix" {% if tx.payment_mode == 'pix' %}selected{% endif %}>PIX</option>
        </select>
      </label>
      <label>Categoria
        <select name="category_id" required>
          {% for c in categories %}
            <option value="{{ c.id }}" {% if c.id == tx.category_id %}selected{% endif %}>{{ c.name }}</option>
          {% endfor %}
        </select>
      </label>
    </div>
    <div class="form-row">
      <label style="flex:1;">Nota
        <textarea name="note" rows="2" maxlength="500">{{ tx.note or '' }}</textarea>
      </label>
    </div>
    <div class="form-actions">
      <button type="submit" class="btn">[ salvar alterações ]</button>
    </div>
  </form>
</div>
{% endblock %}
```

- [ ] **Step 2.6.3: Adicionar link "editar" em `_row.html`**

Arquivo: `app/templates/transactions/_row.html` (substituir inteiro):

```html
<tr>
  <td>{{ tx.date.strftime("%d/%m") }}</td>
  <td><a href="/lancamentos/{{ tx.id }}/editar" style="color:var(--text);">{{ tx.description }}</a></td>
  <td>{{ tx.category.name }}</td>
  <td>{{ tx.source.name }}</td>
  <td><span class="pill mode-{{ tx.payment_mode }}">{{ tx.payment_mode }}</span></td>
  <td class="num">R$ {{ "%.2f" | format(tx.amount) | replace(".", ",") }}</td>
  <td>
    <form method="post" action="/lancamentos/{{ tx.id }}/delete" onsubmit="return confirm('Apagar este lançamento?')" style="display:inline;">
      <button type="submit" class="btn danger" style="padding:4px 8px; font-size:9px;">×</button>
    </form>
  </td>
</tr>
```

- [ ] **Step 2.6.4: Rebuild + testar edição**

```bash
docker compose up -d --build web
# clique na descrição de um lançamento na lista e altere valor → salvar
```

Expected: alteração refletida na lista.

- [ ] **Step 2.6.5: Commit e push**

```bash
git add app/routers/transactions.py app/templates/transactions/
git commit -m "feat: edição de lançamento com formulário pré-preenchido"
git push origin main
```

---

**Marco M2 alcançado:** CRUD completo de lançamentos avulsos com filtros por mês/fonte/categoria/texto. Continua em M3.

---

## Milestone 3 — Ciclo de fatura do cartão de crédito

### Task 3.1: Função pura `fatura_due_month` (TDD rigoroso)

**Files:**
- Create: `app/services/fatura.py`
- Create: `tests/services/test_fatura.py`

- [ ] **Step 3.1.1: Escrever os testes primeiro (TDD — vão falhar)**

Arquivo: `tests/services/test_fatura.py`

```python
from datetime import date

import pytest

from app.services.fatura import fatura_due_month


# Caso "normal": compra antes do fechamento → fatura do mês corrente (venc. mês seguinte)
def test_purchase_before_closing_lands_in_current_month_invoice():
    # Fechamento dia 4, vencimento dia 10
    # Compra dia 03/abr → fatura fecha 04/abr → vence 10/abr
    assert fatura_due_month(date(2026, 4, 3), closing_day=4, due_day=10) == date(2026, 4, 10)


def test_purchase_on_closing_day_still_current_cycle():
    # Compra dia 04/abr (dia de fechamento) → ainda entra na fatura que fecha 04/abr
    assert fatura_due_month(date(2026, 4, 4), closing_day=4, due_day=10) == date(2026, 4, 10)


def test_purchase_day_after_closing_rolls_to_next_cycle():
    # Compra dia 05/abr → fatura fecha 04/mai → vence 10/mai
    assert fatura_due_month(date(2026, 4, 5), closing_day=4, due_day=10) == date(2026, 5, 10)


def test_purchase_late_in_month_rolls_to_next_cycle():
    # Compra dia 30/abr → fatura fecha 04/mai → vence 10/mai
    assert fatura_due_month(date(2026, 4, 30), closing_day=4, due_day=10) == date(2026, 5, 10)


# Virada de ano
def test_december_purchase_after_closing_rolls_to_january():
    # Compra 15/dez → fatura fecha 04/jan/27 → vence 10/jan/27
    assert fatura_due_month(date(2026, 12, 15), closing_day=4, due_day=10) == date(2027, 1, 10)


def test_december_purchase_before_closing_stays_in_december():
    # Compra 02/dez → fatura fecha 04/dez → vence 10/dez
    assert fatura_due_month(date(2026, 12, 2), closing_day=4, due_day=10) == date(2026, 12, 10)


# Diferentes configurações de fechamento/vencimento
def test_custom_closing_and_due():
    # Fechamento 20, vencimento 05 (do mês seguinte ao próximo)
    # Compra 19/abr → fatura fecha 20/abr → vence 05/mai
    assert fatura_due_month(date(2026, 4, 19), closing_day=20, due_day=5) == date(2026, 5, 5)
    # Compra 21/abr → fatura fecha 20/mai → vence 05/jun
    assert fatura_due_month(date(2026, 4, 21), closing_day=20, due_day=5) == date(2026, 6, 5)


# Fevereiro (mês curto)
def test_february_edge_28_days():
    # Compra 28/fev → fecha 04/mar → vence 10/mar
    assert fatura_due_month(date(2026, 2, 28), closing_day=4, due_day=10) == date(2026, 3, 10)


# Validações
def test_invalid_closing_day_raises():
    with pytest.raises(ValueError):
        fatura_due_month(date(2026, 4, 1), closing_day=32, due_day=10)


def test_invalid_due_day_raises():
    with pytest.raises(ValueError):
        fatura_due_month(date(2026, 4, 1), closing_day=4, due_day=0)
```

- [ ] **Step 3.1.2: Rodar os testes — devem falhar por módulo inexistente**

```bash
docker compose run --rm web pytest tests/services/test_fatura.py -v
```

Expected: falha com `ModuleNotFoundError: No module named 'app.services.fatura'`.

- [ ] **Step 3.1.3: Implementar a função pura**

Arquivo: `app/services/fatura.py`

```python
"""Cálculo do ciclo de fatura de cartão de crédito.

O ciclo depende de dois parâmetros da fonte:
- closing_day: dia em que a fatura "fecha" (compras posteriores vão à próxima).
- due_day: dia em que a fatura vence.

Regra: se a data da compra é <= dia de fechamento do mês, a fatura fecha naquele
mês e vence naquele mesmo mês (no dia do vencimento). Caso contrário, fecha no
mês seguinte e vence no mês seguinte.

Na prática para um cartão com fech=4, venc=10:
- Compra 03/abr → fecha 04/abr → vence 10/abr
- Compra 05/abr → fecha 04/mai → vence 10/mai
"""
from datetime import date


def _add_months(base: date, months: int) -> date:
    """Retorna a data `base` acrescida de `months` meses (mantendo o dia)."""
    month_index = base.month - 1 + months
    year = base.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, base.day)


def fatura_due_month(
    transaction_date: date, closing_day: int, due_day: int
) -> date:
    """Retorna a data (ano, mês, dia) de vencimento da fatura.

    Args:
        transaction_date: data da compra.
        closing_day: dia do mês em que a fatura fecha (1..28).
        due_day: dia do mês em que a fatura vence (1..28).

    Returns:
        Data de vencimento da fatura que engloba `transaction_date`.
    """
    if not (1 <= closing_day <= 28):
        raise ValueError("closing_day deve estar entre 1 e 28")
    if not (1 <= due_day <= 28):
        raise ValueError("due_day deve estar entre 1 e 28")

    if transaction_date.day <= closing_day:
        # Fatura fecha no próprio mês; vence no mesmo mês (ou no seguinte se due < closing).
        base_month = transaction_date.replace(day=1)
    else:
        # Fatura só fecha no próximo mês.
        base_month = _add_months(transaction_date.replace(day=1), 1)

    # Determinar o mês de vencimento em relação ao fechamento
    if due_day >= closing_day:
        # Vencimento depois do fechamento → mesmo mês do fechamento
        due = base_month.replace(day=due_day)
    else:
        # Vencimento antes do dia de fechamento → mês seguinte
        due = _add_months(base_month, 1).replace(day=due_day)

    return due
```

- [ ] **Step 3.1.4: Rodar os testes novamente**

```bash
docker compose run --rm web pytest tests/services/test_fatura.py -v
```

Expected: **10 testes PASS**.

- [ ] **Step 3.1.5: Commit e push**

```bash
git add app/services/fatura.py tests/services/test_fatura.py
git commit -m "feat: função pura fatura_due_month com testes de casos de borda"
git push origin main
```

---

### Task 3.2: Coluna derivada `due_date` via property em Transaction

**Files:**
- Modify: `app/models/transaction.py`
- Modify: `app/models/source.py` (verify closing_day/due_day types)
- Create: `tests/services/test_transaction_due_date.py`

- [ ] **Step 3.2.1: Escrever teste que o lançamento sabe calcular seu `due_date`**

Arquivo: `tests/services/test_transaction_due_date.py`

```python
from datetime import date
from decimal import Decimal

from app.models import Source, Transaction


def _make_source(db, **overrides):
    base = {"slug": "x", "name": "X", "kind": "hybrid", "closing_day": 4, "due_day": 10}
    base.update(overrides)
    s = Source(**base)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def test_debit_transaction_due_date_equals_transaction_date(db):
    src = _make_source(db)
    tx = Transaction(
        description="x", amount=Decimal("10"), date=date(2026, 4, 15),
        source_id=src.id, category_id=1, payment_mode="debit",
    )
    assert tx.compute_due_date(src) == date(2026, 4, 15)


def test_pix_transaction_due_date_equals_transaction_date(db):
    src = _make_source(db)
    tx = Transaction(
        description="x", amount=Decimal("10"), date=date(2026, 4, 15),
        source_id=src.id, category_id=1, payment_mode="pix",
    )
    assert tx.compute_due_date(src) == date(2026, 4, 15)


def test_credit_before_closing_goes_to_same_month_invoice(db):
    src = _make_source(db, closing_day=4, due_day=10)
    tx = Transaction(
        description="x", amount=Decimal("10"), date=date(2026, 4, 3),
        source_id=src.id, category_id=1, payment_mode="credit",
    )
    assert tx.compute_due_date(src) == date(2026, 4, 10)


def test_credit_after_closing_goes_to_next_month_invoice(db):
    src = _make_source(db, closing_day=4, due_day=10)
    tx = Transaction(
        description="x", amount=Decimal("10"), date=date(2026, 4, 5),
        source_id=src.id, category_id=1, payment_mode="credit",
    )
    assert tx.compute_due_date(src) == date(2026, 5, 10)


def test_credit_without_source_cycle_falls_back_to_date(db):
    # Fonte sem closing/due (ex. VA/VT) não deveria ter credit; se acontecer,
    # faz fallback para a data da compra.
    src = _make_source(db, closing_day=None, due_day=None, kind="debit")
    tx = Transaction(
        description="x", amount=Decimal("10"), date=date(2026, 4, 5),
        source_id=src.id, category_id=1, payment_mode="credit",
    )
    assert tx.compute_due_date(src) == date(2026, 4, 5)
```

- [ ] **Step 3.2.2: Rodar teste — vai falhar por método inexistente**

```bash
docker compose run --rm web pytest tests/services/test_transaction_due_date.py -v
```

Expected: `AttributeError: 'Transaction' object has no attribute 'compute_due_date'`.

- [ ] **Step 3.2.3: Adicionar método `compute_due_date` em `Transaction`**

Editar `app/models/transaction.py` — adicionar no final da classe:

```python
    def compute_due_date(self, source: "Source") -> "date":
        """Retorna o dia em que este lançamento efetivamente impacta o caixa.

        - debit/pix → a própria data da compra.
        - credit → data de vencimento da fatura, se a fonte tiver ciclo configurado.
                   Se a fonte não tiver closing/due_day, faz fallback para a data.
        """
        from app.services.fatura import fatura_due_month

        if self.payment_mode in ("debit", "pix"):
            return self.date
        # credit
        if source.closing_day is None or source.due_day is None:
            return self.date
        return fatura_due_month(self.date, source.closing_day, source.due_day)
```

- [ ] **Step 3.2.4: Rodar testes novamente**

```bash
docker compose run --rm web pytest tests/services/test_transaction_due_date.py -v
```

Expected: 5 testes PASS.

- [ ] **Step 3.2.5: Commit e push**

```bash
git add app/models/transaction.py tests/services/test_transaction_due_date.py
git commit -m "feat: Transaction.compute_due_date aplica ciclo de fatura em credit"
git push origin main
```

---

### Task 3.3: Exibir "devido em" (due_date) na lista de lançamentos

**Files:**
- Modify: `app/services/transactions.py` (retornar due_date junto)
- Modify: `app/templates/transactions/_row.html`
- Modify: `app/templates/transactions/list.html`

- [ ] **Step 3.3.1: Carregar relações Source nas queries do service**

Editar `app/services/transactions.py` — importar `joinedload`:

```python
from sqlalchemy.orm import Session, joinedload
```

E atualizar `list_all` para incluir eager loading:

```python
def list_all(
    db: Session,
    *,
    year: int | None = None,
    month: int | None = None,
    source_id: int | None = None,
    category_id: int | None = None,
    text: str | None = None,
    limit: int | None = None,
) -> list[Transaction]:
    stmt = select(Transaction).options(
        joinedload(Transaction.source),
        joinedload(Transaction.category),
    )
    if year is not None and month is not None:
        start = date(year, month, 1)
        end_day = monthrange(year, month)[1]
        end = date(year, month, end_day)
        stmt = stmt.where(Transaction.date >= start, Transaction.date <= end)
    if source_id is not None:
        stmt = stmt.where(Transaction.source_id == source_id)
    if category_id is not None:
        stmt = stmt.where(Transaction.category_id == category_id)
    if text:
        stmt = stmt.where(Transaction.description.ilike(f"%{text}%"))
    stmt = stmt.order_by(Transaction.date.desc(), Transaction.id.desc())
    if limit is not None:
        stmt = stmt.limit(limit)
    return list(db.execute(stmt).scalars().all())
```

- [ ] **Step 3.3.2: Atualizar `_row.html` para mostrar devido em**

Arquivo: `app/templates/transactions/_row.html`

```html
<tr>
  <td>{{ tx.date.strftime("%d/%m") }}</td>
  <td><a href="/lancamentos/{{ tx.id }}/editar" style="color:var(--text);">{{ tx.description }}</a></td>
  <td>{{ tx.category.name }}</td>
  <td>{{ tx.source.name }}</td>
  <td><span class="pill mode-{{ tx.payment_mode }}">{{ tx.payment_mode }}</span></td>
  <td class="due">
    {% set due = tx.compute_due_date(tx.source) %}
    {% if due != tx.date %}
      <span class="due-shift">→ {{ due.strftime("%d/%m") }}</span>
    {% else %}
      <span class="dim">—</span>
    {% endif %}
  </td>
  <td class="num">R$ {{ "%.2f" | format(tx.amount) | replace(".", ",") }}</td>
  <td>
    <form method="post" action="/lancamentos/{{ tx.id }}/delete" onsubmit="return confirm('Apagar este lançamento?')" style="display:inline;">
      <button type="submit" class="btn danger" style="padding:4px 8px; font-size:9px;">×</button>
    </form>
  </td>
</tr>
```

- [ ] **Step 3.3.3: Atualizar cabeçalho da tabela em `list.html`**

Substituir o `<thead>` de `app/templates/transactions/list.html`:

```html
    <thead>
      <tr><th>Data</th><th>Descrição</th><th>Categoria</th><th>Fonte</th><th>Modo</th><th>Devido em</th><th>Valor</th><th></th></tr>
    </thead>
```

E ajustar o `<td colspan>` do empty row para `colspan="8"`:

```html
<tr><td colspan="8" class="empty">Sem lançamentos neste filtro.</td></tr>
```

- [ ] **Step 3.3.4: CSS para `.due`**

Anexar ao final de `app/static/css/app.css`:

```css
.tx-table td.due { font-size: 11px; color: var(--muted); }
.due-shift { color: var(--primary); }
.dim { color: var(--dim); }
```

- [ ] **Step 3.3.5: Rebuild + criar um lançamento `credit` e conferir a coluna**

```bash
docker compose up -d --build web
# criar um lançamento credit data 05/abr → a coluna "Devido em" deve mostrar "→ 10/05"
```

- [ ] **Step 3.3.6: Commit e push**

```bash
git add app/services/transactions.py app/templates/transactions/ app/static/css/app.css
git commit -m "feat: coluna 'devido em' mostrando vencimento da fatura para credito"
git push origin main
```

---

**Marco M3 alcançado:** ciclo de fatura implementado e visualmente aparente na lista. Continua em M4.

---

## Milestone 4 — Dashboard v1

### Task 4.1: Service de agregados do dashboard (TDD)

**Files:**
- Create: `app/services/dashboard.py`
- Create: `tests/services/test_dashboard_service.py`

- [ ] **Step 4.1.1: Escrever testes do serviço (vão falhar)**

Arquivo: `tests/services/test_dashboard_service.py`

```python
from datetime import date
from decimal import Decimal

import pytest

from app.services import dashboard as svc
from app.services import transactions as tx_svc
from app.services.seed import seed_all


@pytest.fixture
def seeded(db):
    seed_all(db)
    return db


def _tx(**over):
    base = {
        "description": "x", "amount": Decimal("100"),
        "date": date(2026, 4, 15), "source_id": 1, "category_id": 2,
        "payment_mode": "debit", "type": "expense",
    }
    base.update(over)
    return base


def test_month_totals_sums_expenses_of_the_month(seeded):
    tx_svc.create(seeded, _tx(amount=Decimal("100"), date=date(2026, 4, 1)))
    tx_svc.create(seeded, _tx(amount=Decimal("250"), date=date(2026, 4, 20)))
    tx_svc.create(seeded, _tx(amount=Decimal("80"), date=date(2026, 3, 31)))
    out = svc.month_overview(seeded, year=2026, month=4)
    assert out["total_expense"] == Decimal("350.00")


def test_month_totals_separates_income(seeded):
    tx_svc.create(seeded, _tx(type="expense", amount=Decimal("300")))
    tx_svc.create(seeded, _tx(type="income", amount=Decimal("8500"),
                              payment_mode="pix", date=date(2026, 4, 5)))
    out = svc.month_overview(seeded, year=2026, month=4)
    assert out["total_expense"] == Decimal("300.00")
    assert out["total_income"] == Decimal("8500.00")


def test_top_categories_returns_sorted_limited(seeded):
    tx_svc.create(seeded, _tx(category_id=1, amount=Decimal("1800")))  # Moradia
    tx_svc.create(seeded, _tx(category_id=2, amount=Decimal("890")))   # Mercado
    tx_svc.create(seeded, _tx(category_id=3, amount=Decimal("410")))   # Transporte
    tx_svc.create(seeded, _tx(category_id=5, amount=Decimal("320")))   # Lazer
    tx_svc.create(seeded, _tx(category_id=9, amount=Decimal("50")))    # Outros
    out = svc.top_categories(seeded, year=2026, month=4, limit=4)
    names = [r["name"] for r in out]
    assert names == ["Moradia", "Mercado", "Transporte", "Lazer"]
    assert out[0]["total"] == Decimal("1800.00")


def test_by_source_distribution(seeded):
    tx_svc.create(seeded, _tx(source_id=1, amount=Decimal("1000")))
    tx_svc.create(seeded, _tx(source_id=2, amount=Decimal("200")))
    tx_svc.create(seeded, _tx(source_id=3, amount=Decimal("0.01")))
    out = svc.by_source(seeded, year=2026, month=4)
    totals = {r["slug"]: r["total"] for r in out}
    assert totals["conta-principal"] == Decimal("1000.00")
    assert totals["va"] == Decimal("200.00")


def test_month_overview_includes_counts(seeded):
    tx_svc.create(seeded, _tx(amount=Decimal("10")))
    tx_svc.create(seeded, _tx(amount=Decimal("20")))
    out = svc.month_overview(seeded, year=2026, month=4)
    assert out["count"] == 2
```

- [ ] **Step 4.1.2: Rodar — falha por módulo inexistente**

```bash
docker compose run --rm web pytest tests/services/test_dashboard_service.py -v
```

Expected: `ModuleNotFoundError`.

- [ ] **Step 4.1.3: Implementar o service**

Arquivo: `app/services/dashboard.py`

```python
from calendar import monthrange
from datetime import date
from decimal import Decimal
from typing import TypedDict

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Category, Source, Transaction


class CategoryRow(TypedDict):
    category_id: int
    name: str
    total: Decimal


class SourceRow(TypedDict):
    source_id: int
    slug: str
    name: str
    total: Decimal


class MonthOverview(TypedDict):
    year: int
    month: int
    total_expense: Decimal
    total_income: Decimal
    count: int


def _month_bounds(year: int, month: int) -> tuple[date, date]:
    end_day = monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, end_day)


def month_overview(db: Session, *, year: int, month: int) -> MonthOverview:
    start, end = _month_bounds(year, month)
    totals = db.execute(
        select(
            Transaction.type,
            func.coalesce(func.sum(Transaction.amount), 0),
            func.count(Transaction.id),
        )
        .where(Transaction.date >= start, Transaction.date <= end)
        .where(Transaction.status == "confirmed")
        .group_by(Transaction.type)
    ).all()
    expense = Decimal("0.00")
    income = Decimal("0.00")
    count = 0
    for t, total, n in totals:
        count += n
        if t == "income":
            income = Decimal(total).quantize(Decimal("0.01"))
        else:
            expense = Decimal(total).quantize(Decimal("0.01"))
    return {
        "year": year, "month": month,
        "total_expense": expense, "total_income": income, "count": count,
    }


def top_categories(
    db: Session, *, year: int, month: int, limit: int = 5
) -> list[CategoryRow]:
    start, end = _month_bounds(year, month)
    rows = db.execute(
        select(
            Category.id, Category.name,
            func.coalesce(func.sum(Transaction.amount), 0).label("total"),
        )
        .join(Transaction, Transaction.category_id == Category.id)
        .where(Transaction.date >= start, Transaction.date <= end)
        .where(Transaction.status == "confirmed", Transaction.type == "expense")
        .group_by(Category.id, Category.name)
        .order_by(func.sum(Transaction.amount).desc())
        .limit(limit)
    ).all()
    return [
        {"category_id": row.id, "name": row.name,
         "total": Decimal(row.total).quantize(Decimal("0.01"))}
        for row in rows
    ]


def by_source(db: Session, *, year: int, month: int) -> list[SourceRow]:
    start, end = _month_bounds(year, month)
    rows = db.execute(
        select(
            Source.id, Source.slug, Source.name,
            func.coalesce(func.sum(Transaction.amount), 0).label("total"),
        )
        .join(Transaction, Transaction.source_id == Source.id)
        .where(Transaction.date >= start, Transaction.date <= end)
        .where(Transaction.status == "confirmed", Transaction.type == "expense")
        .group_by(Source.id, Source.slug, Source.name)
        .order_by(func.sum(Transaction.amount).desc())
    ).all()
    return [
        {"source_id": row.id, "slug": row.slug, "name": row.name,
         "total": Decimal(row.total).quantize(Decimal("0.01"))}
        for row in rows
    ]
```

- [ ] **Step 4.1.4: Rodar testes → devem passar**

```bash
docker compose run --rm web pytest tests/services/test_dashboard_service.py -v
```

Expected: 5 testes PASS.

- [ ] **Step 4.1.5: Commit e push**

```bash
git add app/services/dashboard.py tests/services/test_dashboard_service.py
git commit -m "feat: service dashboard com month_overview, top_categories e by_source"
git push origin main
```

---

### Task 4.2: Route do dashboard + template completo

**Files:**
- Create: `app/routers/dashboard.py`
- Modify: `app/templates/dashboard.html`
- Modify: `app/main.py`

- [ ] **Step 4.2.1: Criar `app/routers/dashboard.py`**

Arquivo: `app/routers/dashboard.py`

```python
from datetime import date
from decimal import Decimal
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.deps import get_db
from app.services import dashboard as svc

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(tags=["dashboard"])


def _days_in_month(year: int, month: int) -> int:
    from calendar import monthrange
    return monthrange(year, month)[1]


@router.get("/", response_class=HTMLResponse)
def dashboard_view(
    request: Request,
    db: Session = Depends(get_db),
    year: int | None = None,
    month: int | None = None,
) -> HTMLResponse:
    today = date.today()
    y = year or today.year
    m = month or today.month

    overview = svc.month_overview(db, year=y, month=m)
    top_cats = svc.top_categories(db, year=y, month=m, limit=5)
    sources = svc.by_source(db, year=y, month=m)

    total_spent = overview["total_expense"]
    income = overview["total_income"]
    projected_balance = income - total_spent

    days_total = _days_in_month(y, m)
    day_today = today.day if (today.year == y and today.month == m) else days_total
    burn_per_day = (
        (total_spent / Decimal(day_today)).quantize(Decimal("0.01"))
        if day_today > 0 else Decimal("0.00")
    )

    return templates.TemplateResponse(
        request, "dashboard.html",
        {
            "active_nav": "dashboard",
            "page_title": "Dashboard",
            "year": y, "month": m,
            "overview": overview,
            "top_categories": top_cats,
            "sources": sources,
            "total_spent": total_spent,
            "income": income,
            "projected_balance": projected_balance,
            "burn_per_day": burn_per_day,
            "today": today,
        },
    )
```

- [ ] **Step 4.2.2: Registrar router e remover rota `/` antiga de `main.py`**

Arquivo: `app/main.py`

```python
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.db import SessionLocal
from app.routers import dashboard as dashboard_router
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

app.include_router(dashboard_router.router)
app.include_router(transactions_router.router)


@app.get("/health", response_class=HTMLResponse)
def health() -> str:
    return "<h1>ok</h1>"
```

- [ ] **Step 4.2.3: Substituir `app/templates/dashboard.html` com layout completo**

Arquivo: `app/templates/dashboard.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="header">
  <div>
    <h1>Dashboard<span class="blink">▊</span></h1>
    <div class="subtitle">{{ "%02d" | format(month) }}/{{ year }} · {{ overview.count }} lançamento(s) · atualizado em tempo real</div>
  </div>
  <div class="actions">
    <a class="btn secondary" href="/lancamentos">[ L ] lançamentos</a>
    <a class="btn" href="/lancamentos/novo">[ + ] adicionar</a>
  </div>
</div>

<div class="content">

  <!-- HERO -->
  <div class="hero">
    <div>
      <div class="k">▸ mês corrente · gasto acumulado</div>
      <div class="hero-num">R$ {{ "%.2f" | format(total_spent) | replace(".", ",") }}</div>
      <div class="prog"><div style="width: {{ (100 * total_spent / 5000) | round(1) if total_spent else 0 }}%"></div></div>
      <div class="prog-lbl">
        <span>{{ (100 * total_spent / 5000) | round(1) if total_spent else 0 }}% do alvo (stub)</span>
        <span>ALVO R$ 5.000,00</span>
        <span>dia {{ today.day }}/{{ "%02d" | format(month) }}</span>
      </div>
    </div>
    <div class="metrics">
      <div class="m ok">
        <div class="lbl">Receita</div>
        <div class="val ok">R$ {{ "%.2f" | format(income) | replace(".", ",") }}</div>
      </div>
      <div class="m pu">
        <div class="lbl">Saldo previsto</div>
        <div class="val pu">R$ {{ "%.2f" | format(projected_balance) | replace(".", ",") }}</div>
      </div>
      <div class="m">
        <div class="lbl">Queima / dia</div>
        <div class="val">R$ {{ "%.2f" | format(burn_per_day) | replace(".", ",") }}</div>
      </div>
      <div class="m warn">
        <div class="lbl">Alertas</div>
        <div class="val warn">{{ 0 }}</div>
      </div>
    </div>
  </div>

  <!-- GRID 3 -->
  <div class="grid-3">
    <div class="pnl">
      <div class="pnl-h"><span>categorias</span><span class="tag">top 5</span></div>
      <div class="pnl-b">
        {% for cat in top_categories %}
          <div class="line">
            <span class="nm">{{ cat.name }}</span>
            <span class="pct">{{ (100 * cat.total / total_spent) | round(0) | int if total_spent else 0 }}%</span>
            <span class="vl">R$ {{ "%.2f" | format(cat.total) | replace(".", ",") }}</span>
          </div>
        {% else %}
          <div class="line"><span class="nm dim">sem gastos este mês</span><span></span><span></span></div>
        {% endfor %}
      </div>
    </div>

    <div class="pnl">
      <div class="pnl-h"><span>fontes</span><span class="tag">ativas</span></div>
      <div class="pnl-b">
        {% for s in sources %}
          <div class="line">
            <span class="nm">{{ s.name }}</span>
            <span class="pct">{{ (100 * s.total / total_spent) | round(0) | int if total_spent else 0 }}%</span>
            <span class="vl">R$ {{ "%.2f" | format(s.total) | replace(".", ",") }}</span>
          </div>
        {% else %}
          <div class="line"><span class="nm dim">sem gastos este mês</span><span></span><span></span></div>
        {% endfor %}
      </div>
    </div>

    <div class="pnl">
      <div class="pnl-h"><span>sinais</span><span class="tag">live</span></div>
      <div class="pnl-b">
        <div class="line info"><span class="nm">Alertas</span><span class="pct"></span><span class="vl">implementado em M7</span></div>
        <div class="line info"><span class="nm">Metas</span><span class="pct"></span><span class="vl">implementado em M8</span></div>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 4.2.4: Anexar estilos do dashboard (hero, grid-3) ao CSS**

Anexar ao final de `app/static/css/app.css`:

```css
/* ========== DASHBOARD ========== */
.hero {
  border: 1px solid var(--border); background: var(--bg-2);
  padding: 16px 20px;
  display: grid; grid-template-columns: 1.4fr 1fr; gap: 28px;
  position: relative; overflow: hidden;
}
.hero::before {
  content: ""; position: absolute; top: 0; right: 0; width: 360px; height: 100%;
  background: radial-gradient(ellipse at 100% 50%, rgba(192,132,252,0.08), transparent 60%);
  pointer-events: none;
}
.hero > * { position: relative; z-index: 1; }
.hero .k { font-size: 10px; color: var(--muted); letter-spacing: 0.24em; text-transform: uppercase; margin-bottom: 4px; }
.hero .hero-num {
  font-size: 50px; font-weight: 500; color: var(--primary); line-height: 1;
  letter-spacing: -0.015em; font-variant-numeric: tabular-nums;
  text-shadow: 0 0 22px var(--primary-glow);
}
.hero .prog { margin-top: 12px; height: 6px; background: var(--bg-4); position: relative; overflow: hidden; }
.hero .prog > div { height: 100%; background: linear-gradient(90deg, var(--primary-3), var(--primary), var(--primary-soft)); box-shadow: 0 0 10px var(--primary-glow); }
.hero .prog-lbl { display: flex; justify-content: space-between; margin-top: 6px; font-size: 10px; color: var(--muted); letter-spacing: 0.1em; flex-wrap: wrap; gap: 4px; }
.hero .metrics { display: grid; grid-template-columns: 1fr 1fr; gap: 10px 18px; }
.hero .m { padding-left: 10px; border-left: 2px solid var(--border); }
.hero .m.ok { border-left-color: var(--ok); }
.hero .m.warn { border-left-color: var(--warn); }
.hero .m.pu { border-left-color: var(--primary); }
.hero .m .lbl { font-size: 9px; color: var(--muted); letter-spacing: 0.25em; text-transform: uppercase; }
.hero .m .val { margin-top: 2px; font-size: 16px; font-weight: 500; color: var(--text); font-variant-numeric: tabular-nums; }
.hero .m .val.ok { color: var(--ok); }
.hero .m .val.warn { color: var(--warn); }
.hero .m .val.pu { color: var(--primary); }

.grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 18px; }
.pnl { border: 1px solid var(--border); background: var(--bg-2); }
.pnl-h {
  padding: 12px 18px; background: var(--bg-3); border-bottom: 1px solid var(--border);
  display: flex; justify-content: space-between; align-items: center;
  font-size: 11.5px; color: var(--muted); letter-spacing: 0.24em; text-transform: uppercase;
}
.pnl-h .tag { color: var(--primary); font-weight: 500; }
.pnl-b { padding: 10px 18px 16px; }
.line {
  display: grid; grid-template-columns: 1fr auto auto; gap: 14px; align-items: baseline;
  padding: 12px 0; font-variant-numeric: tabular-nums;
  border-bottom: 1px dashed rgba(255,255,255,0.06);
  font-size: 14px;
}
.line:last-child { border-bottom: none; }
.line .nm { color: var(--text); }
.line .pct { color: var(--muted); font-size: 11px; min-width: 46px; text-align: right; }
.line .vl { color: var(--primary); font-weight: 500; text-align: right; min-width: 108px; font-size: 14px; }
.line.warn .nm::before { content: "⚠ "; color: var(--warn); }
.line.ok .nm::before { content: "✓ "; color: var(--ok); }
.line.info .nm::before { content: "● "; color: var(--info); }

@media (max-width: 1199px) {
  .hero { grid-template-columns: 1fr; }
  .grid-3 { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 767px) {
  .hero { padding: 14px; }
  .hero .hero-num { font-size: 36px; }
  .hero .metrics { grid-template-columns: 1fr 1fr; }
  .grid-3 { grid-template-columns: 1fr; }
  .pnl-b { padding: 8px 14px 12px; }
  .line { font-size: 13px; }
  .line .vl { font-size: 13px; min-width: auto; }
}
```

- [ ] **Step 4.2.5: Rebuild + validar**

```bash
docker compose up -d --build web
# abra http://localhost:8765 — criar alguns lançamentos e ver a agregação
```

Expected: dashboard exibe hero com número principal, metrics (receita/saldo/queima/alertas), e os 3 painéis (Categorias, Fontes, Sinais placeholder). Redimensionar para ver responsividade (< 1200px: grid 2col, < 768px: empilhado).

- [ ] **Step 4.2.6: Commit e push**

```bash
git add app/routers/dashboard.py app/templates/dashboard.html app/main.py app/static/css/app.css
git commit -m "feat: dashboard v1 com hero, metrics, grid-3 e responsividade"
git push origin main
```

---

**Marco M4 alcançado:** dashboard funcional conectado a dados reais. Continua em M5.

---

## Milestone 5 — Parcelamentos

### Task 5.1: Modelo `InstallmentPlan` e migration

**Files:**
- Create: `app/models/installment_plan.py`
- Modify: `app/models/__init__.py`
- Create: `migrations/versions/0003_installment_plans.py`

- [ ] **Step 5.1.1: Criar `app/models/installment_plan.py`**

Arquivo: `app/models/installment_plan.py`

```python
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class InstallmentPlan(Base, TimestampMixin):
    __tablename__ = "installment_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    installments_count: Mapped[int] = mapped_column(Integer, nullable=False)
    installment_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    first_purchase_date: Mapped[date] = mapped_column(Date, nullable=False)

    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)

    active: Mapped[bool] = mapped_column(default=True, nullable=False)

    source = relationship("Source")
    category = relationship("Category")
```

- [ ] **Step 5.1.2: Atualizar `app/models/__init__.py`**

```python
from app.models.base import Base
from app.models.category import Category
from app.models.installment_plan import InstallmentPlan
from app.models.source import Source
from app.models.transaction import Transaction

__all__ = ["Base", "Category", "InstallmentPlan", "Source", "Transaction"]
```

- [ ] **Step 5.1.3: Gerar e aplicar migration**

```bash
docker compose run --rm web alembic revision --autogenerate -m "installment_plans"
# renomear arquivo em migrations/versions/ para 0003_installment_plans.py
docker compose run --rm web alembic upgrade head
```

- [ ] **Step 5.1.4: Commit e push**

```bash
git add app/models/installment_plan.py app/models/__init__.py migrations/versions/0003_installment_plans.py
git commit -m "feat: modelo InstallmentPlan com total, contagem e data de compra"
git push origin main
```

---

### Task 5.2: Service de parcelamentos (TDD — lógica crítica)

**Files:**
- Create: `app/services/installments.py`
- Create: `app/schemas/installment.py`
- Create: `tests/services/test_installments_service.py`

- [ ] **Step 5.2.1: Criar schema `app/schemas/installment.py`**

Arquivo: `app/schemas/installment.py`

```python
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class InstallmentPlanCreate(BaseModel):
    description: str = Field(min_length=1, max_length=200)
    installments_count: int = Field(ge=2, le=120)
    first_purchase_date: date
    source_id: int
    category_id: int

    # Uma das duas formas:
    input_mode: Literal["total", "per_installment"]
    total_amount: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    installment_amount: Decimal | None = Field(default=None, gt=0, decimal_places=2)

    @model_validator(mode="after")
    def _check_amounts(self) -> "InstallmentPlanCreate":
        if self.input_mode == "total":
            if self.total_amount is None:
                raise ValueError("total_amount obrigatório quando input_mode='total'")
        elif self.input_mode == "per_installment":
            if self.installment_amount is None:
                raise ValueError(
                    "installment_amount obrigatório quando input_mode='per_installment'"
                )
        return self
```

- [ ] **Step 5.2.2: Escrever os testes do service**

Arquivo: `tests/services/test_installments_service.py`

```python
from datetime import date
from decimal import Decimal

import pytest

from app.models import Source, Transaction
from app.services import installments as svc
from app.services.seed import seed_all


@pytest.fixture
def seeded(db):
    seed_all(db)
    return db


def _principal(db):
    return db.query(Source).filter_by(slug="conta-principal").first()


def test_create_from_total_splits_evenly(seeded):
    plan = svc.create_plan(seeded, {
        "description": "iPhone 14",
        "installments_count": 12,
        "first_purchase_date": date(2026, 4, 3),
        "source_id": _principal(seeded).id,
        "category_id": 1,
        "input_mode": "total",
        "total_amount": Decimal("6240.00"),
    })
    assert plan.id is not None
    assert plan.total_amount == Decimal("6240.00")
    assert plan.installment_amount == Decimal("520.00")


def test_create_from_per_installment_multiplies(seeded):
    plan = svc.create_plan(seeded, {
        "description": "Sofá",
        "installments_count": 6,
        "first_purchase_date": date(2026, 4, 15),
        "source_id": _principal(seeded).id,
        "category_id": 1,
        "input_mode": "per_installment",
        "installment_amount": Decimal("350.00"),
    })
    assert plan.total_amount == Decimal("2100.00")
    assert plan.installment_amount == Decimal("350.00")


def test_create_plan_generates_N_transactions(seeded):
    plan = svc.create_plan(seeded, {
        "description": "iPhone",
        "installments_count": 12,
        "first_purchase_date": date(2026, 4, 3),  # antes do fechamento (dia 4)
        "source_id": _principal(seeded).id,
        "category_id": 1,
        "input_mode": "total",
        "total_amount": Decimal("6240.00"),
    })
    txs = seeded.query(Transaction).filter_by(origin="installment",
                                                origin_ref_id=plan.id).all()
    assert len(txs) == 12
    assert all(tx.amount == Decimal("520.00") for tx in txs)
    assert all(tx.payment_mode == "credit" for tx in txs)
    assert all(tx.origin == "installment" for tx in txs)


def test_first_installment_respects_closing_before(seeded):
    # compra 03/abr → fatura 10/abr (porque fecha dia 4 e 03 <= 04)
    plan = svc.create_plan(seeded, {
        "description": "a",
        "installments_count": 3,
        "first_purchase_date": date(2026, 4, 3),
        "source_id": _principal(seeded).id,
        "category_id": 1,
        "input_mode": "total",
        "total_amount": Decimal("300.00"),
    })
    txs = sorted(
        seeded.query(Transaction).filter_by(origin="installment",
                                              origin_ref_id=plan.id).all(),
        key=lambda t: t.date,
    )
    # As datas dos lançamentos são as datas de vencimento das parcelas
    assert txs[0].date == date(2026, 4, 10)
    assert txs[1].date == date(2026, 5, 10)
    assert txs[2].date == date(2026, 6, 10)


def test_first_installment_respects_closing_after(seeded):
    # compra 05/abr → fatura 10/mai (porque 05 > 04)
    plan = svc.create_plan(seeded, {
        "description": "b",
        "installments_count": 3,
        "first_purchase_date": date(2026, 4, 5),
        "source_id": _principal(seeded).id,
        "category_id": 1,
        "input_mode": "total",
        "total_amount": Decimal("300.00"),
    })
    txs = sorted(
        seeded.query(Transaction).filter_by(origin="installment",
                                              origin_ref_id=plan.id).all(),
        key=lambda t: t.date,
    )
    assert txs[0].date == date(2026, 5, 10)
    assert txs[1].date == date(2026, 6, 10)
    assert txs[2].date == date(2026, 7, 10)


def test_installments_are_projected_until_real_date(seeded):
    plan = svc.create_plan(seeded, {
        "description": "c",
        "installments_count": 3,
        "first_purchase_date": date(2026, 4, 3),
        "source_id": _principal(seeded).id,
        "category_id": 1,
        "input_mode": "total",
        "total_amount": Decimal("300.00"),
    })
    txs = seeded.query(Transaction).filter_by(origin_ref_id=plan.id).all()
    assert all(tx.status == "projected" for tx in txs)


def test_create_on_non_credit_source_raises(seeded):
    va = seeded.query(Source).filter_by(slug="va").first()
    with pytest.raises(ValueError, match="só em fontes com crédito"):
        svc.create_plan(seeded, {
            "description": "x",
            "installments_count": 3,
            "first_purchase_date": date(2026, 4, 1),
            "source_id": va.id,
            "category_id": 1,
            "input_mode": "total",
            "total_amount": Decimal("300.00"),
        })


def test_delete_plan_removes_unconfirmed_transactions(seeded):
    plan = svc.create_plan(seeded, {
        "description": "del",
        "installments_count": 3,
        "first_purchase_date": date(2026, 4, 3),
        "source_id": _principal(seeded).id,
        "category_id": 1,
        "input_mode": "total",
        "total_amount": Decimal("300.00"),
    })
    svc.delete_plan(seeded, plan.id)
    remaining = seeded.query(Transaction).filter_by(origin_ref_id=plan.id).all()
    assert remaining == []


def test_delete_plan_keeps_already_confirmed(seeded):
    plan = svc.create_plan(seeded, {
        "description": "del2",
        "installments_count": 3,
        "first_purchase_date": date(2026, 4, 3),
        "source_id": _principal(seeded).id,
        "category_id": 1,
        "input_mode": "total",
        "total_amount": Decimal("300.00"),
    })
    # Confirmar a primeira parcela manualmente
    first_tx = seeded.query(Transaction).filter_by(origin_ref_id=plan.id).order_by(
        Transaction.date
    ).first()
    first_tx.status = "confirmed"
    seeded.commit()

    svc.delete_plan(seeded, plan.id)

    remaining = seeded.query(Transaction).filter_by(origin_ref_id=plan.id).all()
    assert len(remaining) == 1
    assert remaining[0].status == "confirmed"
```

- [ ] **Step 5.2.3: Rodar testes — devem falhar**

```bash
docker compose run --rm web pytest tests/services/test_installments_service.py -v
```

Expected: falha por módulo inexistente.

- [ ] **Step 5.2.4: Implementar o service**

Arquivo: `app/services/installments.py`

```python
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from sqlalchemy.orm import Session

from app.models import InstallmentPlan, Source, Transaction
from app.services.fatura import fatura_due_month


def _quantize(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _next_due_date(base_due: date, months_ahead: int) -> date:
    """Avança N meses mantendo o dia."""
    month_index = base_due.month - 1 + months_ahead
    year = base_due.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, base_due.day)


def create_plan(db: Session, data: dict[str, Any]) -> InstallmentPlan:
    source = db.get(Source, data["source_id"])
    if source is None:
        raise LookupError(f"Source {data['source_id']} not found")
    if source.closing_day is None or source.due_day is None:
        raise ValueError(
            "Parcelamentos só em fontes com crédito (closing_day + due_day)"
        )

    count = int(data["installments_count"])
    mode = data["input_mode"]
    if mode == "total":
        total = Decimal(data["total_amount"])
        per = _quantize(total / Decimal(count))
    elif mode == "per_installment":
        per = Decimal(data["installment_amount"])
        total = _quantize(per * Decimal(count))
    else:
        raise ValueError(f"input_mode inválido: {mode}")

    plan = InstallmentPlan(
        description=data["description"],
        total_amount=_quantize(total),
        installments_count=count,
        installment_amount=per,
        first_purchase_date=data["first_purchase_date"],
        source_id=source.id,
        category_id=data["category_id"],
        active=True,
    )
    db.add(plan)
    db.flush()  # garante plan.id

    # Calcula a data de vencimento da primeira parcela
    first_due = fatura_due_month(
        plan.first_purchase_date, source.closing_day, source.due_day
    )
    for i in range(count):
        due = _next_due_date(first_due, i)
        tx = Transaction(
            description=f"{plan.description} — parcela {i + 1}/{count}",
            amount=per,
            date=due,
            source_id=source.id,
            category_id=plan.category_id,
            payment_mode="credit",
            type="expense",
            origin="installment",
            origin_ref_id=plan.id,
            status="projected",
        )
        db.add(tx)

    db.commit()
    db.refresh(plan)
    return plan


def list_plans(db: Session, *, active_only: bool = True) -> list[InstallmentPlan]:
    q = db.query(InstallmentPlan)
    if active_only:
        q = q.filter(InstallmentPlan.active.is_(True))
    return q.order_by(InstallmentPlan.first_purchase_date.desc()).all()


def get_plan(db: Session, plan_id: int) -> InstallmentPlan:
    plan = db.get(InstallmentPlan, plan_id)
    if plan is None:
        raise LookupError(f"InstallmentPlan {plan_id} not found")
    return plan


def delete_plan(db: Session, plan_id: int) -> None:
    plan = get_plan(db, plan_id)
    # Apagar apenas parcelas projetadas (não confirmadas)
    db.query(Transaction).filter(
        Transaction.origin_ref_id == plan.id,
        Transaction.origin == "installment",
        Transaction.status == "projected",
    ).delete(synchronize_session=False)
    db.delete(plan)
    db.commit()


def confirm_installment(db: Session, tx_id: int) -> Transaction:
    tx = db.get(Transaction, tx_id)
    if tx is None or tx.origin != "installment":
        raise LookupError(f"Installment transaction {tx_id} not found")
    tx.status = "confirmed"
    db.commit()
    db.refresh(tx)
    return tx
```

- [ ] **Step 5.2.5: Rodar testes → devem passar**

```bash
docker compose run --rm web pytest tests/services/test_installments_service.py -v
```

Expected: 9 testes PASS.

- [ ] **Step 5.2.6: Commit e push**

```bash
git add app/services/installments.py app/schemas/installment.py tests/services/test_installments_service.py
git commit -m "feat: service de parcelamentos com geração de N parcelas respeitando fatura"
git push origin main
```

---

### Task 5.3: Router `/parcelados` com lista e criação

**Files:**
- Create: `app/routers/installments.py`
- Create: `app/templates/installments/list.html`
- Create: `app/templates/installments/new.html`
- Modify: `app/main.py`

- [ ] **Step 5.3.1: Criar `app/routers/installments.py`**

Arquivo: `app/routers/installments.py`

```python
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
    # só fontes com crédito
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
```

- [ ] **Step 5.3.2: Criar `app/templates/installments/list.html`**

Arquivo: `app/templates/installments/list.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="header">
  <div>
    <h1>Parcelados<span class="blink">▊</span></h1>
    <div class="subtitle">{{ plans | length }} plano(s) cadastrado(s)</div>
  </div>
  <div class="actions">
    <a class="btn" href="/parcelados/novo">[ + ] novo parcelamento</a>
  </div>
</div>

<div class="content">
  <table class="tx-table">
    <thead>
      <tr><th>Descrição</th><th>Compra em</th><th>Parcelas</th><th>Valor/parc</th><th>Total</th><th>Status</th><th></th></tr>
    </thead>
    <tbody>
      {% for p in plans %}
        <tr>
          <td><a href="/parcelados/{{ p.id }}" style="color: var(--text);">{{ p.description }}</a></td>
          <td>{{ p.first_purchase_date.strftime("%d/%m/%Y") }}</td>
          <td>{{ p.installments_count }}x</td>
          <td class="num">R$ {{ "%.2f" | format(p.installment_amount) | replace(".", ",") }}</td>
          <td class="num">R$ {{ "%.2f" | format(p.total_amount) | replace(".", ",") }}</td>
          <td>
            {% if p.active %}<span class="pill mode-credit">ativo</span>
            {% else %}<span class="pill">arquivado</span>{% endif %}
          </td>
          <td>
            <form method="post" action="/parcelados/{{ p.id }}/delete" onsubmit="return confirm('Apagar plano e parcelas projetadas?')" style="display:inline;">
              <button type="submit" class="btn danger" style="padding:4px 8px; font-size:9px;">×</button>
            </form>
          </td>
        </tr>
      {% else %}
        <tr><td colspan="7" class="empty">Nenhum parcelamento cadastrado.</td></tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% endblock %}
```

- [ ] **Step 5.3.3: Criar `app/templates/installments/new.html`**

Arquivo: `app/templates/installments/new.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="header">
  <div>
    <h1>Novo parcelamento<span class="blink">▊</span></h1>
    <div class="subtitle">crédito apenas · primeira parcela respeita fechamento</div>
  </div>
  <div class="actions">
    <a class="btn secondary" href="/parcelados">[ ← ] voltar</a>
  </div>
</div>

<div class="content">
  <form method="post" action="/parcelados/novo" class="form-card" id="inst-form">
    <div class="form-row">
      <label style="flex:1;">Descrição
        <input type="text" name="description" required maxlength="200" autofocus>
      </label>
      <label>Data da compra
        <input type="date" name="first_purchase_date" value="{{ today }}" required>
      </label>
    </div>

    <div class="form-row">
      <label>Fonte (crédito)
        <select name="source_id" required>
          {% for s in sources %}<option value="{{ s.id }}">{{ s.name }}</option>{% endfor %}
        </select>
      </label>
      <label>Categoria
        <select name="category_id" required>
          {% for c in categories %}<option value="{{ c.id }}">{{ c.name }}</option>{% endfor %}
        </select>
      </label>
      <label>Nº parcelas
        <input type="number" name="installments_count" value="12" min="2" max="120" required>
      </label>
    </div>

    <div class="form-row" style="gap: 20px; align-items: center;">
      <label style="flex-direction: row; align-items: center; gap: 8px;">
        <input type="radio" name="input_mode" value="total" checked onchange="toggleMode(this.value)"> informar total
      </label>
      <label style="flex-direction: row; align-items: center; gap: 8px;">
        <input type="radio" name="input_mode" value="per_installment" onchange="toggleMode(this.value)"> informar valor da parcela
      </label>
    </div>

    <div class="form-row" id="row-total">
      <label style="flex:1;">Valor total (R$)
        <input type="text" name="total_amount" placeholder="0,00">
      </label>
    </div>

    <div class="form-row" id="row-per" style="display:none;">
      <label style="flex:1;">Valor de cada parcela (R$)
        <input type="text" name="installment_amount" placeholder="0,00">
      </label>
    </div>

    <div class="form-actions">
      <button type="submit" class="btn">[ criar parcelamento ]</button>
    </div>
  </form>
</div>

<script>
  function toggleMode(mode) {
    document.getElementById("row-total").style.display = mode === "total" ? "" : "none";
    document.getElementById("row-per").style.display = mode === "per_installment" ? "" : "none";
  }
</script>
{% endblock %}
```

- [ ] **Step 5.3.4: Criar `app/templates/installments/detail.html`**

Arquivo: `app/templates/installments/detail.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="header">
  <div>
    <h1>{{ plan.description }}<span class="blink">▊</span></h1>
    <div class="subtitle">
      {{ plan.installments_count }}x de R$ {{ "%.2f" | format(plan.installment_amount) | replace(".", ",") }}
      · total R$ {{ "%.2f" | format(plan.total_amount) | replace(".", ",") }}
      · compra em {{ plan.first_purchase_date.strftime("%d/%m/%Y") }}
    </div>
  </div>
  <div class="actions">
    <a class="btn secondary" href="/parcelados">[ ← ] voltar</a>
  </div>
</div>

<div class="content">
  <table class="tx-table">
    <thead>
      <tr><th>#</th><th>Vencimento</th><th>Valor</th><th>Status</th><th></th></tr>
    </thead>
    <tbody>
      {% for tx in installments %}
        <tr>
          <td>{{ loop.index }}/{{ plan.installments_count }}</td>
          <td>{{ tx.date.strftime("%d/%m/%Y") }}</td>
          <td class="num">R$ {{ "%.2f" | format(tx.amount) | replace(".", ",") }}</td>
          <td>
            {% if tx.status == "confirmed" %}
              <span class="pill mode-pix">confirmada</span>
            {% else %}
              <span class="pill mode-credit">projetada</span>
            {% endif %}
          </td>
          <td>
            {% if tx.status == "projected" %}
              <form method="post" action="/parcelados/tx/{{ tx.id }}/confirm" style="display:inline;">
                <button type="submit" class="btn secondary" style="padding:4px 10px; font-size:9px;">confirmar</button>
              </form>
            {% endif %}
          </td>
        </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% endblock %}
```

- [ ] **Step 5.3.5: Registrar router em `app/main.py`**

Adicionar import e `include_router`:

```python
from app.routers import installments as installments_router
# ...
app.include_router(installments_router.router)
```

- [ ] **Step 5.3.6: Rebuild + testar end-to-end**

```bash
docker compose up -d --build web
# abra http://localhost:8765/parcelados
# clique [+ novo parcelamento]
# preencha: descrição "iPhone 14", 12 parcelas, data hoje, total 6240
# deve criar e listar; clicar no nome mostra as 12 parcelas projetadas
```

- [ ] **Step 5.3.7: Commit e push**

```bash
git add app/routers/installments.py app/templates/installments/ app/main.py
git commit -m "feat: páginas de parcelamentos (lista, novo, detalhe, confirmação)"
git push origin main
```

---

**Marco M5 alcançado:** parcelamentos funcionais com as duas formas de entrada (total/parcela) e geração automática de N lançamentos respeitando o ciclo de fatura. Continua em M6.

---

## Milestone 6 — Gastos fixos recorrentes

### Task 6.1: Modelo `FixedRule` e migration

**Files:**
- Create: `app/models/fixed_rule.py`
- Modify: `app/models/__init__.py`
- Create: `migrations/versions/0004_fixed_rules.py`

- [ ] **Step 6.1.1: Criar `app/models/fixed_rule.py`**

Arquivo: `app/models/fixed_rule.py`

```python
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class FixedRule(Base, TimestampMixin):
    __tablename__ = "fixed_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    expected_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    # monthly | annual | weekly | every_n_months
    recurrence: Mapped[str] = mapped_column(String(24), nullable=False)
    interval_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    day_of_month: Mapped[int | None] = mapped_column(Integer, nullable=True)
    day_of_week: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 0=mon..6=sun
    anchor_month: Mapped[int | None] = mapped_column(Integer, nullable=True)  # para annual

    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    payment_mode: Mapped[str] = mapped_column(String(16), nullable=False)  # credit|debit|pix
    type: Mapped[str] = mapped_column(String(16), nullable=False, default="expense")

    active_from: Mapped[date] = mapped_column(Date, nullable=False)
    active_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    archived: Mapped[bool] = mapped_column(default=False, nullable=False)

    source = relationship("Source")
    category = relationship("Category")
```

- [ ] **Step 6.1.2: Atualizar `app/models/__init__.py`**

```python
from app.models.base import Base
from app.models.category import Category
from app.models.fixed_rule import FixedRule
from app.models.installment_plan import InstallmentPlan
from app.models.source import Source
from app.models.transaction import Transaction

__all__ = [
    "Base", "Category", "FixedRule", "InstallmentPlan", "Source", "Transaction"
]
```

- [ ] **Step 6.1.3: Gerar e aplicar migration**

```bash
docker compose run --rm web alembic revision --autogenerate -m "fixed_rules"
# renomear para 0004_fixed_rules.py
docker compose run --rm web alembic upgrade head
```

- [ ] **Step 6.1.4: Commit e push**

```bash
git add app/models/fixed_rule.py app/models/__init__.py migrations/versions/0004_fixed_rules.py
git commit -m "feat: modelo FixedRule com recorrência flexível (mensal/anual/semanal/N meses)"
git push origin main
```

---

### Task 6.2: Service de projeção de fixos (TDD)

**Files:**
- Create: `app/services/fixed_projection.py`
- Create: `tests/services/test_fixed_projection.py`

- [ ] **Step 6.2.1: Escrever testes (vão falhar)**

Arquivo: `tests/services/test_fixed_projection.py`

```python
from datetime import date
from decimal import Decimal

import pytest

from app.models import FixedRule, Source
from app.services import fixed_projection as svc
from app.services.seed import seed_all


@pytest.fixture
def seeded(db):
    seed_all(db)
    return db


def _mk_rule(db, **overrides):
    principal = db.query(Source).filter_by(slug="conta-principal").first()
    base = {
        "description": "Aluguel",
        "expected_amount": Decimal("1800.00"),
        "recurrence": "monthly",
        "day_of_month": 5,
        "source_id": principal.id,
        "category_id": 1,
        "payment_mode": "debit",
        "type": "expense",
        "active_from": date(2025, 1, 1),
    }
    base.update(overrides)
    rule = FixedRule(**base)
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def test_monthly_projects_one_per_month_in_range(seeded):
    rule = _mk_rule(seeded)  # dia 5, mensal
    occurrences = svc.project_rule(rule, start=date(2026, 4, 1), end=date(2026, 6, 30))
    assert occurrences == [date(2026, 4, 5), date(2026, 5, 5), date(2026, 6, 5)]


def test_monthly_skips_before_active_from(seeded):
    rule = _mk_rule(seeded, active_from=date(2026, 5, 10))
    occurrences = svc.project_rule(rule, start=date(2026, 4, 1), end=date(2026, 6, 30))
    # Somente jun/05 está dentro (mai/05 é antes do active_from 10/05)
    assert occurrences == [date(2026, 6, 5)]


def test_monthly_stops_at_active_until(seeded):
    rule = _mk_rule(seeded, active_until=date(2026, 5, 31))
    occurrences = svc.project_rule(rule, start=date(2026, 4, 1), end=date(2026, 7, 31))
    assert occurrences == [date(2026, 4, 5), date(2026, 5, 5)]


def test_annual_uses_anchor_month(seeded):
    rule = _mk_rule(seeded, recurrence="annual", anchor_month=1, day_of_month=10,
                    description="IPTU")
    occ = svc.project_rule(rule, start=date(2025, 1, 1), end=date(2027, 12, 31))
    assert occ == [date(2025, 1, 10), date(2026, 1, 10), date(2027, 1, 10)]


def test_weekly_projects_each_week(seeded):
    # toda segunda-feira (day_of_week=0)
    rule = _mk_rule(seeded, recurrence="weekly", day_of_week=0, day_of_month=None,
                    active_from=date(2026, 4, 1))
    occ = svc.project_rule(rule, start=date(2026, 4, 1), end=date(2026, 4, 30))
    # segundas de abril/26: 6, 13, 20, 27
    assert occ == [date(2026, 4, 6), date(2026, 4, 13),
                   date(2026, 4, 20), date(2026, 4, 27)]


def test_every_n_months_with_interval_3(seeded):
    rule = _mk_rule(seeded, recurrence="every_n_months", interval_months=3,
                    day_of_month=15, active_from=date(2026, 1, 15))
    occ = svc.project_rule(rule, start=date(2026, 1, 1), end=date(2026, 12, 31))
    assert occ == [date(2026, 1, 15), date(2026, 4, 15),
                   date(2026, 7, 15), date(2026, 10, 15)]


def test_unknown_recurrence_raises(seeded):
    rule = _mk_rule(seeded, recurrence="yearly")  # typo intencional
    with pytest.raises(ValueError, match="recurrence"):
        svc.project_rule(rule, start=date(2026, 1, 1), end=date(2026, 12, 31))
```

- [ ] **Step 6.2.2: Rodar — falham**

```bash
docker compose run --rm web pytest tests/services/test_fixed_projection.py -v
```

- [ ] **Step 6.2.3: Implementar o service**

Arquivo: `app/services/fixed_projection.py`

```python
from calendar import monthrange
from datetime import date, timedelta

from app.models import FixedRule


def _clamp_day(year: int, month: int, day: int) -> date:
    max_day = monthrange(year, month)[1]
    return date(year, month, min(day, max_day))


def _add_months(base: date, months: int) -> date:
    month_index = base.month - 1 + months
    year = base.year + month_index // 12
    month = month_index % 12 + 1
    return _clamp_day(year, month, base.day)


def project_rule(rule: FixedRule, *, start: date, end: date) -> list[date]:
    """Calcula as datas em que a regra fixa ocorre entre start e end (inclusive).

    Não acessa o banco; é uma função pura sobre o modelo.
    """
    if start > end:
        return []

    lower = max(start, rule.active_from)
    upper = end if rule.active_until is None else min(end, rule.active_until)
    if lower > upper:
        return []

    recurrence = rule.recurrence
    results: list[date] = []

    if recurrence == "monthly":
        if rule.day_of_month is None:
            raise ValueError("monthly requer day_of_month")
        cur = _clamp_day(lower.year, lower.month, rule.day_of_month)
        if cur < lower:
            cur = _add_months(cur, 1)
        while cur <= upper:
            if cur >= rule.active_from:
                results.append(cur)
            cur = _add_months(cur, 1)

    elif recurrence == "annual":
        if rule.day_of_month is None or rule.anchor_month is None:
            raise ValueError("annual requer day_of_month e anchor_month")
        for year in range(lower.year, upper.year + 1):
            cur = _clamp_day(year, rule.anchor_month, rule.day_of_month)
            if lower <= cur <= upper and cur >= rule.active_from:
                results.append(cur)

    elif recurrence == "weekly":
        if rule.day_of_week is None:
            raise ValueError("weekly requer day_of_week (0=seg..6=dom)")
        cur = lower
        # Avançar até o próximo day_of_week
        offset = (rule.day_of_week - cur.weekday()) % 7
        cur = cur + timedelta(days=offset)
        while cur <= upper:
            if cur >= rule.active_from:
                results.append(cur)
            cur = cur + timedelta(days=7)

    elif recurrence == "every_n_months":
        if rule.interval_months is None or rule.day_of_month is None:
            raise ValueError("every_n_months requer interval_months e day_of_month")
        # Anchor inicial baseado em active_from
        anchor = _clamp_day(
            rule.active_from.year, rule.active_from.month, rule.day_of_month
        )
        cur = anchor
        while cur < lower:
            cur = _add_months(cur, rule.interval_months)
        while cur <= upper:
            results.append(cur)
            cur = _add_months(cur, rule.interval_months)

    else:
        raise ValueError(f"recurrence inválida: {recurrence}")

    return results
```

- [ ] **Step 6.2.4: Rodar testes → passam**

```bash
docker compose run --rm web pytest tests/services/test_fixed_projection.py -v
```

Expected: 7 testes PASS.

- [ ] **Step 6.2.5: Commit e push**

```bash
git add app/services/fixed_projection.py tests/services/test_fixed_projection.py
git commit -m "feat: projeção de regras fixas (monthly, annual, weekly, every_n_months)"
git push origin main
```

---

### Task 6.3: Service de fixos — CRUD e confirmação

**Files:**
- Create: `app/services/fixed.py`
- Create: `app/schemas/fixed.py`

- [ ] **Step 6.3.1: Criar schema `app/schemas/fixed.py`**

Arquivo: `app/schemas/fixed.py`

```python
from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class FixedRuleCreate(BaseModel):
    description: str = Field(min_length=1, max_length=200)
    expected_amount: Decimal = Field(gt=0, decimal_places=2)
    recurrence: Literal["monthly", "annual", "weekly", "every_n_months"]
    source_id: int
    category_id: int
    payment_mode: Literal["credit", "debit", "pix"]
    type: Literal["expense", "income"] = "expense"
    active_from: date
    active_until: date | None = None
    interval_months: int | None = None
    day_of_month: int | None = Field(default=None, ge=1, le=31)
    day_of_week: int | None = Field(default=None, ge=0, le=6)
    anchor_month: int | None = Field(default=None, ge=1, le=12)

    @model_validator(mode="after")
    def _check_fields(self) -> "FixedRuleCreate":
        r = self.recurrence
        if r == "monthly" and self.day_of_month is None:
            raise ValueError("monthly requer day_of_month")
        if r == "annual" and (self.day_of_month is None or self.anchor_month is None):
            raise ValueError("annual requer day_of_month e anchor_month")
        if r == "weekly" and self.day_of_week is None:
            raise ValueError("weekly requer day_of_week")
        if r == "every_n_months" and (
            self.interval_months is None or self.day_of_month is None
        ):
            raise ValueError("every_n_months requer interval_months e day_of_month")
        return self
```

- [ ] **Step 6.3.2: Criar `app/services/fixed.py`**

Arquivo: `app/services/fixed.py`

```python
from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.models import FixedRule, Transaction
from app.services.fixed_projection import project_rule


def create_rule(db: Session, data: dict[str, Any]) -> FixedRule:
    rule = FixedRule(**data)
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


def list_rules(db: Session, *, include_archived: bool = False) -> list[FixedRule]:
    q = db.query(FixedRule)
    if not include_archived:
        q = q.filter(FixedRule.archived.is_(False))
    return q.order_by(FixedRule.description).all()


def get_rule(db: Session, rule_id: int) -> FixedRule:
    r = db.get(FixedRule, rule_id)
    if r is None:
        raise LookupError(f"FixedRule {rule_id} not found")
    return r


def archive_rule(db: Session, rule_id: int) -> FixedRule:
    r = get_rule(db, rule_id)
    r.archived = True
    db.commit()
    db.refresh(r)
    return r


def project_month(db: Session, *, year: int, month: int) -> list[dict[str, Any]]:
    """Retorna lista de ocorrências de fixos para o mês dado, identificando
    quais já têm lançamento confirmado (e o valor real, se houver)."""
    from calendar import monthrange

    start = date(year, month, 1)
    end = date(year, month, monthrange(year, month)[1])

    rules = list_rules(db, include_archived=False)
    results: list[dict[str, Any]] = []
    for rule in rules:
        for occ_date in project_rule(rule, start=start, end=end):
            confirmed = (
                db.query(Transaction)
                .filter(
                    Transaction.origin == "fixed",
                    Transaction.origin_ref_id == rule.id,
                    Transaction.date == occ_date,
                    Transaction.status == "confirmed",
                )
                .first()
            )
            results.append({
                "rule_id": rule.id,
                "description": rule.description,
                "date": occ_date,
                "expected_amount": rule.expected_amount,
                "actual_amount": confirmed.amount if confirmed else None,
                "confirmed_tx_id": confirmed.id if confirmed else None,
                "source_id": rule.source_id,
                "category_id": rule.category_id,
                "payment_mode": rule.payment_mode,
                "type": rule.type,
            })
    return results


def confirm_occurrence(
    db: Session,
    *,
    rule_id: int,
    occ_date: date,
    actual_amount: Decimal,
) -> Transaction:
    """Cria ou atualiza o lançamento confirmado de uma ocorrência."""
    rule = get_rule(db, rule_id)
    existing = (
        db.query(Transaction)
        .filter(
            Transaction.origin == "fixed",
            Transaction.origin_ref_id == rule.id,
            Transaction.date == occ_date,
        )
        .first()
    )
    if existing:
        existing.amount = actual_amount
        existing.status = "confirmed"
        db.commit()
        db.refresh(existing)
        return existing
    tx = Transaction(
        description=rule.description,
        amount=actual_amount,
        date=occ_date,
        source_id=rule.source_id,
        category_id=rule.category_id,
        payment_mode=rule.payment_mode,
        type=rule.type,
        origin="fixed",
        origin_ref_id=rule.id,
        status="confirmed",
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx
```

- [ ] **Step 6.3.3: Commit e push**

```bash
git add app/services/fixed.py app/schemas/fixed.py
git commit -m "feat: service de fixos com CRUD, projeção mensal e confirmação"
git push origin main
```

---

### Task 6.4: Router `/fixos` com lista, novo e confirmação mensal

**Files:**
- Create: `app/routers/fixed.py`
- Create: `app/templates/fixed/list.html`
- Create: `app/templates/fixed/new.html`
- Create: `app/templates/fixed/monthly.html`
- Modify: `app/main.py`

- [ ] **Step 6.4.1: Criar `app/routers/fixed.py`**

Arquivo: `app/routers/fixed.py`

```python
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
```

- [ ] **Step 6.4.2: Criar `app/templates/fixed/list.html`**

Arquivo: `app/templates/fixed/list.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="header">
  <div>
    <h1>Gastos fixos<span class="blink">▊</span></h1>
    <div class="subtitle">{{ rules | length }} regra(s) · {{ "%02d" | format(month) }}/{{ year }} tem {{ occurrences | length }} ocorrência(s)</div>
  </div>
  <div class="actions">
    <a class="btn" href="/fixos/novo">[ + ] novo fixo</a>
  </div>
</div>

<div class="content">
  <h3 style="color: var(--muted); letter-spacing: 0.22em; text-transform: uppercase; font-size: 11px; margin-bottom: 10px;">▸ Ocorrências deste mês</h3>
  <table class="tx-table">
    <thead>
      <tr><th>Data</th><th>Descrição</th><th>Esperado</th><th>Real</th><th>Ação</th></tr>
    </thead>
    <tbody>
      {% for o in occurrences %}
        <tr>
          <td>{{ o.date.strftime("%d/%m") }}</td>
          <td>{{ o.description }}</td>
          <td class="num">R$ {{ "%.2f" | format(o.expected_amount) | replace(".", ",") }}</td>
          <td class="num">
            {% if o.actual_amount %}R$ {{ "%.2f" | format(o.actual_amount) | replace(".", ",") }}
            {% else %}<span class="dim">—</span>{% endif %}
          </td>
          <td>
            {% if not o.confirmed_tx_id %}
            <form method="post" action="/fixos/confirm" style="display:flex; gap:6px;">
              <input type="hidden" name="rule_id" value="{{ o.rule_id }}">
              <input type="hidden" name="occ_date" value="{{ o.date.isoformat() }}">
              <input type="text" name="actual_amount" placeholder="{{ '%.2f' | format(o.expected_amount) }}" style="width: 90px; background: var(--bg); color: var(--text); border: 1px solid var(--border-2); padding: 4px 6px;">
              <button type="submit" class="btn" style="padding: 4px 10px; font-size: 9px;">confirmar</button>
            </form>
            {% else %}
              <span class="pill mode-pix">✓ confirmado</span>
            {% endif %}
          </td>
        </tr>
      {% else %}
        <tr><td colspan="5" class="empty">Nenhuma ocorrência neste mês.</td></tr>
      {% endfor %}
    </tbody>
  </table>

  <h3 style="color: var(--muted); letter-spacing: 0.22em; text-transform: uppercase; font-size: 11px; margin: 24px 0 10px;">▸ Regras cadastradas</h3>
  <table class="tx-table">
    <thead>
      <tr><th>Descrição</th><th>Recorrência</th><th>Esperado</th><th>Fonte</th><th>Status</th><th></th></tr>
    </thead>
    <tbody>
      {% for r in rules %}
        <tr>
          <td>{{ r.description }}</td>
          <td>{{ r.recurrence }}{% if r.day_of_month %} · dia {{ r.day_of_month }}{% endif %}</td>
          <td class="num">R$ {{ "%.2f" | format(r.expected_amount) | replace(".", ",") }}</td>
          <td>{{ r.source.name }}</td>
          <td>{% if r.archived %}<span class="pill">arquivada</span>{% else %}<span class="pill mode-pix">ativa</span>{% endif %}</td>
          <td>
            {% if not r.archived %}
            <form method="post" action="/fixos/{{ r.id }}/archive" onsubmit="return confirm('Arquivar esta regra?')" style="display:inline;">
              <button type="submit" class="btn secondary" style="padding:4px 8px; font-size:9px;">arquivar</button>
            </form>
            {% endif %}
          </td>
        </tr>
      {% else %}
        <tr><td colspan="6" class="empty">Nenhuma regra cadastrada.</td></tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% endblock %}
```

- [ ] **Step 6.4.3: Criar `app/templates/fixed/new.html`**

Arquivo: `app/templates/fixed/new.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="header">
  <div>
    <h1>Novo fixo<span class="blink">▊</span></h1>
    <div class="subtitle">recorrência: mensal, anual, semanal ou a cada N meses</div>
  </div>
  <div class="actions">
    <a class="btn secondary" href="/fixos">[ ← ] voltar</a>
  </div>
</div>

<div class="content">
  <form method="post" action="/fixos/novo" class="form-card">
    <div class="form-row">
      <label style="flex:1;">Descrição
        <input type="text" name="description" required maxlength="200" autofocus>
      </label>
      <label>Valor esperado (R$)
        <input type="text" name="expected_amount" placeholder="0,00" required>
      </label>
    </div>

    <div class="form-row">
      <label>Tipo
        <select name="type">
          <option value="expense" selected>gasto</option>
          <option value="income">receita</option>
        </select>
      </label>
      <label>Fonte
        <select name="source_id" required>
          {% for s in sources %}<option value="{{ s.id }}">{{ s.name }}</option>{% endfor %}
        </select>
      </label>
      <label>Modo
        <select name="payment_mode" required>
          <option value="debit">débito</option>
          <option value="credit">crédito</option>
          <option value="pix">PIX</option>
        </select>
      </label>
      <label>Categoria
        <select name="category_id" required>
          {% for c in categories %}<option value="{{ c.id }}">{{ c.name }}</option>{% endfor %}
        </select>
      </label>
    </div>

    <div class="form-row">
      <label>Recorrência
        <select name="recurrence" id="recurrence-sel" onchange="updateRecurrenceFields()">
          <option value="monthly" selected>mensal</option>
          <option value="annual">anual</option>
          <option value="weekly">semanal</option>
          <option value="every_n_months">a cada N meses</option>
        </select>
      </label>
      <label id="fld-dom">Dia do mês
        <input type="number" name="day_of_month" min="1" max="31" value="5">
      </label>
      <label id="fld-dow" style="display:none;">Dia da semana (0=seg..6=dom)
        <input type="number" name="day_of_week" min="0" max="6">
      </label>
      <label id="fld-anchor" style="display:none;">Mês do ano (1..12)
        <input type="number" name="anchor_month" min="1" max="12">
      </label>
      <label id="fld-interval" style="display:none;">Intervalo (meses)
        <input type="number" name="interval_months" min="1" max="24" value="3">
      </label>
    </div>

    <div class="form-row">
      <label>Ativa a partir de
        <input type="date" name="active_from" value="{{ today }}" required>
      </label>
      <label>Ativa até (opcional)
        <input type="date" name="active_until">
      </label>
    </div>

    <div class="form-actions">
      <button type="submit" class="btn">[ criar regra ]</button>
    </div>
  </form>
</div>

<script>
function updateRecurrenceFields() {
  const r = document.getElementById("recurrence-sel").value;
  document.getElementById("fld-dom").style.display = (r === "monthly" || r === "annual" || r === "every_n_months") ? "" : "none";
  document.getElementById("fld-dow").style.display = r === "weekly" ? "" : "none";
  document.getElementById("fld-anchor").style.display = r === "annual" ? "" : "none";
  document.getElementById("fld-interval").style.display = r === "every_n_months" ? "" : "none";
}
</script>
{% endblock %}
```

- [ ] **Step 6.4.4: Registrar router em `app/main.py`**

```python
from app.routers import fixed as fixed_router
# ...
app.include_router(fixed_router.router)
```

- [ ] **Step 6.4.5: Rebuild + testar**

```bash
docker compose up -d --build web
# criar regra: Aluguel, R$ 1800, mensal, dia 5, débito, Conta Principal
# na lista, confirmar valor real "1850,00" → move para confirmado
```

- [ ] **Step 6.4.6: Commit e push**

```bash
git add app/routers/fixed.py app/templates/fixed/ app/main.py
git commit -m "feat: páginas de fixos (lista, novo, confirmação mensal de valores reais)"
git push origin main
```

---

**Marco M6 alcançado:** fixos recorrentes com 4 tipos de recorrência e fluxo de confirmação de valor real. Continua em M7.

---

## Milestone 7 — Orçamento + Alertas

### Task 7.1: Modelo `Budget` e migration

**Files:**
- Create: `app/models/budget.py`
- Modify: `app/models/__init__.py`
- Create: `migrations/versions/0005_budgets.py`

- [ ] **Step 7.1.1: Criar `app/models/budget.py`**

Arquivo: `app/models/budget.py`

```python
from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Budget(Base, TimestampMixin):
    """Orçamento alvo.

    Quando category_id é NULL → alvo total mensal.
    Quando category_id tem valor → alvo daquela categoria.
    Sempre vale "para todos os meses" (sem override por mês, conforme spec).
    """
    __tablename__ = "budgets"
    __table_args__ = (UniqueConstraint("category_id", name="uq_budget_category"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    scope: Mapped[str] = mapped_column(String(16), nullable=False)  # total|category
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"), nullable=True
    )

    category = relationship("Category")
```

- [ ] **Step 7.1.2: Atualizar `app/models/__init__.py`**

```python
from app.models.base import Base
from app.models.budget import Budget
from app.models.category import Category
from app.models.fixed_rule import FixedRule
from app.models.installment_plan import InstallmentPlan
from app.models.source import Source
from app.models.transaction import Transaction

__all__ = ["Base", "Budget", "Category", "FixedRule", "InstallmentPlan", "Source", "Transaction"]
```

- [ ] **Step 7.1.3: Gerar e aplicar migration**

```bash
docker compose run --rm web alembic revision --autogenerate -m "budgets"
# renomear para 0005_budgets.py
docker compose run --rm web alembic upgrade head
```

- [ ] **Step 7.1.4: Commit e push**

```bash
git add app/models/budget.py app/models/__init__.py migrations/versions/0005_budgets.py
git commit -m "feat: modelo Budget com escopo total ou por categoria"
git push origin main
```

---

### Task 7.2: Service de orçamento (TDD)

**Files:**
- Create: `app/services/budgets.py`
- Create: `tests/services/test_budgets_service.py`

- [ ] **Step 7.2.1: Escrever testes**

Arquivo: `tests/services/test_budgets_service.py`

```python
from decimal import Decimal

import pytest

from app.services import budgets as svc
from app.services.seed import seed_all


@pytest.fixture
def seeded(db):
    seed_all(db)
    return db


def test_set_total_budget_creates_row(seeded):
    b = svc.set_total(seeded, Decimal("5000.00"))
    assert b.scope == "total"
    assert b.amount == Decimal("5000.00")
    assert b.category_id is None


def test_set_total_budget_updates_existing(seeded):
    svc.set_total(seeded, Decimal("5000.00"))
    b = svc.set_total(seeded, Decimal("6000.00"))
    assert b.amount == Decimal("6000.00")
    assert len(svc.list_all(seeded)) == 1


def test_set_category_budget(seeded):
    b = svc.set_category(seeded, category_id=5, amount=Decimal("400.00"))
    assert b.scope == "category"
    assert b.category_id == 5
    assert b.amount == Decimal("400.00")


def test_get_total_returns_none_if_not_set(seeded):
    assert svc.get_total(seeded) is None


def test_get_total_returns_amount(seeded):
    svc.set_total(seeded, Decimal("5000.00"))
    assert svc.get_total(seeded) == Decimal("5000.00")


def test_get_category_returns_dict(seeded):
    svc.set_category(seeded, category_id=1, amount=Decimal("1800.00"))
    svc.set_category(seeded, category_id=5, amount=Decimal("400.00"))
    result = svc.get_by_category(seeded)
    assert result[1] == Decimal("1800.00")
    assert result[5] == Decimal("400.00")
```

- [ ] **Step 7.2.2: Rodar — falham**

```bash
docker compose run --rm web pytest tests/services/test_budgets_service.py -v
```

- [ ] **Step 7.2.3: Implementar service**

Arquivo: `app/services/budgets.py`

```python
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import Budget


def list_all(db: Session) -> list[Budget]:
    return db.query(Budget).all()


def set_total(db: Session, amount: Decimal) -> Budget:
    existing = db.query(Budget).filter_by(scope="total", category_id=None).first()
    if existing:
        existing.amount = amount
        db.commit()
        db.refresh(existing)
        return existing
    b = Budget(scope="total", category_id=None, amount=amount)
    db.add(b)
    db.commit()
    db.refresh(b)
    return b


def set_category(db: Session, *, category_id: int, amount: Decimal) -> Budget:
    existing = db.query(Budget).filter_by(scope="category", category_id=category_id).first()
    if existing:
        existing.amount = amount
        db.commit()
        db.refresh(existing)
        return existing
    b = Budget(scope="category", category_id=category_id, amount=amount)
    db.add(b)
    db.commit()
    db.refresh(b)
    return b


def get_total(db: Session) -> Decimal | None:
    b = db.query(Budget).filter_by(scope="total", category_id=None).first()
    return b.amount if b else None


def get_by_category(db: Session) -> dict[int, Decimal]:
    rows = db.query(Budget).filter(Budget.scope == "category").all()
    return {b.category_id: b.amount for b in rows if b.category_id is not None}


def delete_category(db: Session, category_id: int) -> None:
    existing = db.query(Budget).filter_by(scope="category", category_id=category_id).first()
    if existing:
        db.delete(existing)
        db.commit()
```

- [ ] **Step 7.2.4: Rodar testes → passam**

```bash
docker compose run --rm web pytest tests/services/test_budgets_service.py -v
```

Expected: 6 testes PASS.

- [ ] **Step 7.2.5: Commit e push**

```bash
git add app/services/budgets.py tests/services/test_budgets_service.py
git commit -m "feat: service de orçamento (total + por categoria)"
git push origin main
```

---

### Task 7.3: Service de alertas (TDD)

**Files:**
- Create: `app/services/alerts.py`
- Create: `tests/services/test_alerts_service.py`

- [ ] **Step 7.3.1: Escrever testes**

Arquivo: `tests/services/test_alerts_service.py`

```python
from datetime import date
from decimal import Decimal

import pytest

from app.services import alerts as svc
from app.services import budgets as bud_svc
from app.services import transactions as tx_svc
from app.services.seed import seed_all


@pytest.fixture
def seeded(db):
    seed_all(db)
    return db


def _tx(**over):
    base = {
        "description": "x", "amount": Decimal("100"),
        "date": date(2026, 4, 15), "source_id": 1, "category_id": 2,
        "payment_mode": "debit", "type": "expense",
    }
    base.update(over)
    return base


def test_no_alerts_when_under_80pct(seeded):
    bud_svc.set_category(seeded, category_id=5, amount=Decimal("400"))
    tx_svc.create(seeded, _tx(category_id=5, amount=Decimal("200")))  # 50%
    out = svc.evaluate(seeded, year=2026, month=4)
    assert out == []


def test_alert_when_category_reaches_80pct(seeded):
    bud_svc.set_category(seeded, category_id=5, amount=Decimal("400"))
    tx_svc.create(seeded, _tx(category_id=5, amount=Decimal("320")))  # 80%
    out = svc.evaluate(seeded, year=2026, month=4)
    assert len(out) == 1
    assert out[0]["level"] == "warn"
    assert "Lazer" in out[0]["message"]
    assert out[0]["kind"] == "category_threshold"


def test_alert_when_total_reaches_90pct(seeded):
    bud_svc.set_total(seeded, Decimal("1000"))
    tx_svc.create(seeded, _tx(amount=Decimal("900")))  # 90%
    out = svc.evaluate(seeded, year=2026, month=4)
    kinds = [a["kind"] for a in out]
    assert "total_threshold" in kinds


def test_no_alert_when_no_budget_set(seeded):
    tx_svc.create(seeded, _tx(amount=Decimal("99999")))
    out = svc.evaluate(seeded, year=2026, month=4)
    assert out == []


def test_alert_level_err_above_100pct(seeded):
    bud_svc.set_category(seeded, category_id=5, amount=Decimal("400"))
    tx_svc.create(seeded, _tx(category_id=5, amount=Decimal("450")))  # 112%
    out = svc.evaluate(seeded, year=2026, month=4)
    assert out[0]["level"] == "err"
```

- [ ] **Step 7.3.2: Implementar service**

Arquivo: `app/services/alerts.py`

```python
from decimal import Decimal
from typing import TypedDict

from sqlalchemy.orm import Session

from app.models import Category
from app.services import budgets as bud_svc
from app.services import dashboard as dash_svc

CATEGORY_THRESHOLD = Decimal("0.80")
TOTAL_THRESHOLD = Decimal("0.90")


class Alert(TypedDict):
    kind: str  # category_threshold | total_threshold
    level: str  # warn | err
    message: str
    pct: float
    ref_id: int | None


def evaluate(db: Session, *, year: int, month: int) -> list[Alert]:
    alerts: list[Alert] = []

    # Alertas por categoria
    cat_budgets = bud_svc.get_by_category(db)
    if cat_budgets:
        cats = {c.id: c.name for c in db.query(Category).all()}
        top = dash_svc.top_categories(db, year=year, month=month, limit=50)
        spent_by_cat = {row["category_id"]: row["total"] for row in top}
        for cat_id, alvo in cat_budgets.items():
            spent = spent_by_cat.get(cat_id, Decimal("0.00"))
            if alvo <= 0:
                continue
            ratio = Decimal(spent) / alvo
            if ratio >= CATEGORY_THRESHOLD:
                level = "err" if ratio > Decimal("1.0") else "warn"
                alerts.append({
                    "kind": "category_threshold",
                    "level": level,
                    "message": f"{cats.get(cat_id, '?')} — {int(ratio * 100)}% do alvo",
                    "pct": float(ratio * 100),
                    "ref_id": cat_id,
                })

    # Alerta total
    total_budget = bud_svc.get_total(db)
    if total_budget and total_budget > 0:
        overview = dash_svc.month_overview(db, year=year, month=month)
        ratio = overview["total_expense"] / total_budget
        if ratio >= TOTAL_THRESHOLD:
            level = "err" if ratio > Decimal("1.0") else "warn"
            alerts.append({
                "kind": "total_threshold",
                "level": level,
                "message": f"Orçamento total — {int(ratio * 100)}%",
                "pct": float(ratio * 100),
                "ref_id": None,
            })

    return alerts
```

- [ ] **Step 7.3.3: Rodar testes → passam**

```bash
docker compose run --rm web pytest tests/services/test_alerts_service.py -v
```

Expected: 5 testes PASS.

- [ ] **Step 7.3.4: Commit e push**

```bash
git add app/services/alerts.py tests/services/test_alerts_service.py
git commit -m "feat: service de alertas avaliando thresholds de orçamento (80/90/100%)"
git push origin main
```

---

### Task 7.4: Integrar alertas ao dashboard + página de configuração

**Files:**
- Modify: `app/routers/dashboard.py`
- Modify: `app/templates/dashboard.html`
- Create: `app/routers/config.py`
- Create: `app/templates/config/system.html`
- Create: `app/templates/config/categories.html`
- Modify: `app/main.py`

- [ ] **Step 7.4.1: Integrar alertas ao dashboard router**

Substituir `app/routers/dashboard.py`:

```python
from datetime import date
from decimal import Decimal
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.deps import get_db
from app.services import alerts as alerts_svc
from app.services import budgets as bud_svc
from app.services import dashboard as svc

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(tags=["dashboard"])


def _days_in_month(year: int, month: int) -> int:
    from calendar import monthrange
    return monthrange(year, month)[1]


@router.get("/", response_class=HTMLResponse)
def dashboard_view(
    request: Request,
    db: Session = Depends(get_db),
    year: int | None = None,
    month: int | None = None,
) -> HTMLResponse:
    today = date.today()
    y = year or today.year
    m = month or today.month

    overview = svc.month_overview(db, year=y, month=m)
    top_cats = svc.top_categories(db, year=y, month=m, limit=5)
    sources = svc.by_source(db, year=y, month=m)
    alerts = alerts_svc.evaluate(db, year=y, month=m)
    total_budget = bud_svc.get_total(db) or Decimal("0.00")

    total_spent = overview["total_expense"]
    income = overview["total_income"]
    projected_balance = income - total_spent

    days_total = _days_in_month(y, m)
    day_today = today.day if (today.year == y and today.month == m) else days_total
    burn_per_day = (
        (total_spent / Decimal(day_today)).quantize(Decimal("0.01"))
        if day_today > 0 else Decimal("0.00")
    )

    budget_ratio = (
        float((total_spent / total_budget) * 100) if total_budget > 0 else 0
    )

    return templates.TemplateResponse(
        request, "dashboard.html",
        {
            "active_nav": "dashboard",
            "page_title": "Dashboard",
            "year": y, "month": m,
            "overview": overview,
            "top_categories": top_cats,
            "sources": sources,
            "alerts": alerts,
            "total_spent": total_spent,
            "total_budget": total_budget,
            "budget_ratio": budget_ratio,
            "income": income,
            "projected_balance": projected_balance,
            "burn_per_day": burn_per_day,
            "today": today,
        },
    )
```

- [ ] **Step 7.4.2: Atualizar `dashboard.html` para usar total_budget e alerts reais**

Substituir `app/templates/dashboard.html`:

```html
{% extends "base.html" %}

{% block content %}
<div class="header">
  <div>
    <h1>Dashboard<span class="blink">▊</span></h1>
    <div class="subtitle">{{ "%02d" | format(month) }}/{{ year }} · {{ overview.count }} lançamento(s)</div>
  </div>
  <div class="actions">
    <a class="btn secondary" href="/lancamentos">[ L ] lançamentos</a>
    <a class="btn" href="/lancamentos/novo">[ + ] adicionar</a>
  </div>
</div>

<div class="content">
  <div class="hero">
    <div>
      <div class="k">▸ mês corrente · gasto acumulado</div>
      <div class="hero-num">R$ {{ "%.2f" | format(total_spent) | replace(".", ",") }}</div>
      <div class="prog"><div style="width: {{ budget_ratio | round(1) }}%"></div></div>
      <div class="prog-lbl">
        <span>{{ budget_ratio | round(1) }}% do alvo</span>
        <span>ALVO R$ {{ "%.2f" | format(total_budget) | replace(".", ",") }}</span>
        <span>dia {{ today.day }}/{{ "%02d" | format(month) }}</span>
      </div>
    </div>
    <div class="metrics">
      <div class="m ok">
        <div class="lbl">Receita</div>
        <div class="val ok">R$ {{ "%.2f" | format(income) | replace(".", ",") }}</div>
      </div>
      <div class="m pu">
        <div class="lbl">Saldo previsto</div>
        <div class="val pu">R$ {{ "%.2f" | format(projected_balance) | replace(".", ",") }}</div>
      </div>
      <div class="m">
        <div class="lbl">Queima / dia</div>
        <div class="val">R$ {{ "%.2f" | format(burn_per_day) | replace(".", ",") }}</div>
      </div>
      <div class="m {% if alerts %}warn{% endif %}">
        <div class="lbl">Alertas</div>
        <div class="val {% if alerts %}warn{% endif %}">{{ alerts | length }}</div>
      </div>
    </div>
  </div>

  <div class="grid-3">
    <div class="pnl">
      <div class="pnl-h"><span>categorias</span><span class="tag">top 5</span></div>
      <div class="pnl-b">
        {% for cat in top_categories %}
          <div class="line">
            <span class="nm">{{ cat.name }}</span>
            <span class="pct">{{ (100 * cat.total / total_spent) | round(0) | int if total_spent else 0 }}%</span>
            <span class="vl">R$ {{ "%.2f" | format(cat.total) | replace(".", ",") }}</span>
          </div>
        {% else %}
          <div class="line"><span class="nm dim">sem gastos este mês</span><span></span><span></span></div>
        {% endfor %}
      </div>
    </div>

    <div class="pnl">
      <div class="pnl-h"><span>fontes</span><span class="tag">ativas</span></div>
      <div class="pnl-b">
        {% for s in sources %}
          <div class="line">
            <span class="nm">{{ s.name }}</span>
            <span class="pct">{{ (100 * s.total / total_spent) | round(0) | int if total_spent else 0 }}%</span>
            <span class="vl">R$ {{ "%.2f" | format(s.total) | replace(".", ",") }}</span>
          </div>
        {% else %}
          <div class="line"><span class="nm dim">sem gastos este mês</span><span></span><span></span></div>
        {% endfor %}
      </div>
    </div>

    <div class="pnl">
      <div class="pnl-h"><span>sinais</span><span class="tag">live</span></div>
      <div class="pnl-b">
        {% for a in alerts %}
          <div class="line {% if a.level == 'err' %}warn{% else %}warn{% endif %}">
            <span class="nm">{{ a.message }}</span>
            <span class="pct">{{ a.pct | round(0) | int }}%</span>
            <span class="vl">{{ a.kind }}</span>
          </div>
        {% else %}
          <div class="line ok"><span class="nm">tudo dentro do alvo</span><span></span><span></span></div>
        {% endfor %}
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 7.4.3: Criar `app/routers/config.py`**

Arquivo: `app/routers/config.py`

```python
from decimal import Decimal, InvalidOperation
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models import Category
from app.services import budgets as bud_svc

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
```

- [ ] **Step 7.4.4: Criar `app/templates/config/system.html`**

Arquivo: `app/templates/config/system.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="header">
  <div>
    <h1>Sistema<span class="blink">▊</span></h1>
    <div class="subtitle">configurações globais</div>
  </div>
</div>

<div class="content">
  <form method="post" action="/config/sistema/budget" class="form-card" style="max-width:440px;">
    <div class="form-row">
      <label style="flex:1;">Orçamento total mensal (R$)
        <input type="text" name="amount" value="{{ '%.2f' | format(total_budget) }}" required>
      </label>
    </div>
    <div class="form-actions">
      <button type="submit" class="btn">[ salvar ]</button>
    </div>
  </form>
</div>
{% endblock %}
```

- [ ] **Step 7.4.5: Criar `app/templates/config/categories.html`**

Arquivo: `app/templates/config/categories.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="header">
  <div>
    <h1>Categorias<span class="blink">▊</span></h1>
    <div class="subtitle">{{ categories | length }} ativa(s) · orçamento por categoria</div>
  </div>
</div>

<div class="content">
  <table class="tx-table">
    <thead>
      <tr><th>Ícone</th><th>Nome</th><th>Slug</th><th>Alvo mensal</th><th></th></tr>
    </thead>
    <tbody>
      {% for c in categories %}
        <tr>
          <td>{{ c.icon or '—' }}</td>
          <td>{{ c.name }}</td>
          <td><code style="font-size:11px; color:var(--muted);">{{ c.slug }}</code></td>
          <td>
            <form method="post" action="/config/categorias/{{ c.id }}/budget" style="display:flex; gap:6px; align-items:center;">
              <input type="text" name="amount" value="{{ '%.2f' | format(budgets_map.get(c.id, 0)) }}" style="width: 100px; background: var(--bg); color: var(--text); border: 1px solid var(--border-2); padding: 4px 6px;">
              <button type="submit" class="btn secondary" style="padding:4px 10px; font-size:9px;">salvar</button>
            </form>
          </td>
          <td></td>
        </tr>
      {% endfor %}
    </tbody>
  </table>

  <h3 style="color: var(--muted); letter-spacing: 0.22em; text-transform: uppercase; font-size: 11px; margin: 24px 0 10px;">▸ Nova categoria</h3>
  <form method="post" action="/config/categorias/novo" class="form-card" style="max-width:560px;">
    <div class="form-row">
      <label>Slug (único, sem espaços)
        <input type="text" name="slug" required maxlength="48" pattern="[a-z0-9-]+">
      </label>
      <label style="flex:1;">Nome
        <input type="text" name="name" required maxlength="80">
      </label>
      <label>Ícone
        <input type="text" name="icon" maxlength="8" placeholder="🎁">
      </label>
    </div>
    <div class="form-actions">
      <button type="submit" class="btn">[ criar ]</button>
    </div>
  </form>
</div>
{% endblock %}
```

- [ ] **Step 7.4.6: Registrar router em `app/main.py`**

```python
from app.routers import config as config_router
# ...
app.include_router(config_router.router)
```

- [ ] **Step 7.4.7: Rebuild + testar fluxo**

```bash
docker compose up -d --build web
# /config/sistema → definir alvo total 5000
# /config/categorias → definir alvo 400 para Lazer
# /lancamentos/novo → gasto 320 em Lazer em 04/2026
# / → conferir: hero mostra % do alvo, grid de sinais mostra "Lazer 80%"
```

- [ ] **Step 7.4.8: Commit e push**

```bash
git add app/routers/dashboard.py app/routers/config.py app/templates/dashboard.html app/templates/config/ app/main.py
git commit -m "feat: orçamento total + por categoria integrado ao dashboard com alertas"
git push origin main
```

---

**Marco M7 alcançado:** orçamento alvo e alertas funcionais no dashboard. Continua em M8.

---

## Milestone 8 — Metas de economia

### Task 8.1: Modelo `Goal` + migration

**Files:**
- Create: `app/models/goal.py`
- Modify: `app/models/__init__.py`
- Create: `migrations/versions/0006_goals.py`

- [ ] **Step 8.1.1: Criar `app/models/goal.py`**

Arquivo: `app/models/goal.py`

```python
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Goal(Base, TimestampMixin):
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    target_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    saved_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)
```

- [ ] **Step 8.1.2: Atualizar `app/models/__init__.py`**

```python
from app.models.base import Base
from app.models.budget import Budget
from app.models.category import Category
from app.models.fixed_rule import FixedRule
from app.models.goal import Goal
from app.models.installment_plan import InstallmentPlan
from app.models.source import Source
from app.models.transaction import Transaction

__all__ = [
    "Base", "Budget", "Category", "FixedRule", "Goal",
    "InstallmentPlan", "Source", "Transaction",
]
```

- [ ] **Step 8.1.3: Gerar e aplicar migration**

```bash
docker compose run --rm web alembic revision --autogenerate -m "goals"
# renomear para 0006_goals.py
docker compose run --rm web alembic upgrade head
```

- [ ] **Step 8.1.4: Commit e push**

```bash
git add app/models/goal.py app/models/__init__.py migrations/versions/0006_goals.py
git commit -m "feat: modelo Goal com target, saved, prazo"
git push origin main
```

---

### Task 8.2: Service de metas (TDD)

**Files:**
- Create: `app/services/goals.py`
- Create: `tests/services/test_goals_service.py`

- [ ] **Step 8.2.1: Escrever testes**

Arquivo: `tests/services/test_goals_service.py`

```python
from datetime import date
from decimal import Decimal

import pytest

from app.services import goals as svc


def test_create_goal(db):
    g = svc.create(db, {
        "title": "Viagem Chile", "target_amount": Decimal("10000.00"),
        "target_date": date(2026, 12, 31),
    })
    assert g.id is not None
    assert g.saved_amount == Decimal("0.00")
    assert g.active is True


def test_add_progress_increments_saved(db):
    g = svc.create(db, {"title": "x", "target_amount": Decimal("1000.00")})
    svc.add_progress(db, g.id, Decimal("200.00"))
    svc.add_progress(db, g.id, Decimal("300.00"))
    g = svc.get(db, g.id)
    assert g.saved_amount == Decimal("500.00")


def test_progress_percentage(db):
    g = svc.create(db, {"title": "x", "target_amount": Decimal("1000.00")})
    svc.add_progress(db, g.id, Decimal("250.00"))
    assert svc.progress_pct(svc.get(db, g.id)) == 25.0


def test_archive_goal(db):
    g = svc.create(db, {"title": "x", "target_amount": Decimal("100")})
    svc.archive(db, g.id)
    assert svc.get(db, g.id).active is False


def test_list_excludes_archived_by_default(db):
    a = svc.create(db, {"title": "ativa", "target_amount": Decimal("100")})
    b = svc.create(db, {"title": "inativa", "target_amount": Decimal("100")})
    svc.archive(db, b.id)
    active = svc.list_all(db)
    assert [g.id for g in active] == [a.id]


def test_get_unknown_raises(db):
    with pytest.raises(LookupError):
        svc.get(db, 999)
```

- [ ] **Step 8.2.2: Rodar — falham**

```bash
docker compose run --rm web pytest tests/services/test_goals_service.py -v
```

- [ ] **Step 8.2.3: Implementar service**

Arquivo: `app/services/goals.py`

```python
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.models import Goal


def create(db: Session, data: dict[str, Any]) -> Goal:
    g = Goal(**data)
    if g.saved_amount is None:
        g.saved_amount = Decimal("0.00")
    db.add(g)
    db.commit()
    db.refresh(g)
    return g


def get(db: Session, goal_id: int) -> Goal:
    g = db.get(Goal, goal_id)
    if g is None:
        raise LookupError(f"Goal {goal_id} not found")
    return g


def list_all(db: Session, *, include_archived: bool = False) -> list[Goal]:
    q = db.query(Goal)
    if not include_archived:
        q = q.filter(Goal.active.is_(True))
    return q.order_by(Goal.target_date.asc().nullslast(), Goal.id.desc()).all()


def add_progress(db: Session, goal_id: int, amount: Decimal) -> Goal:
    g = get(db, goal_id)
    g.saved_amount = (g.saved_amount or Decimal("0.00")) + amount
    db.commit()
    db.refresh(g)
    return g


def update(db: Session, goal_id: int, data: dict[str, Any]) -> Goal:
    g = get(db, goal_id)
    for k, v in data.items():
        if v is not None:
            setattr(g, k, v)
    db.commit()
    db.refresh(g)
    return g


def archive(db: Session, goal_id: int) -> Goal:
    g = get(db, goal_id)
    g.active = False
    db.commit()
    db.refresh(g)
    return g


def progress_pct(goal: Goal) -> float:
    if goal.target_amount == 0:
        return 0.0
    return float((goal.saved_amount / goal.target_amount) * 100)
```

- [ ] **Step 8.2.4: Rodar testes → passam**

```bash
docker compose run --rm web pytest tests/services/test_goals_service.py -v
```

Expected: 6 testes PASS.

- [ ] **Step 8.2.5: Commit e push**

```bash
git add app/services/goals.py tests/services/test_goals_service.py
git commit -m "feat: service de metas com progresso, arquivamento e pct"
git push origin main
```

---

### Task 8.3: Router e UI de `/metas`

**Files:**
- Create: `app/routers/goals.py`
- Create: `app/templates/goals/list.html`
- Create: `app/templates/goals/new.html`
- Modify: `app/main.py`

- [ ] **Step 8.3.1: Criar `app/routers/goals.py`**

Arquivo: `app/routers/goals.py`

```python
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
```

- [ ] **Step 8.3.2: Criar `app/templates/goals/list.html`**

Arquivo: `app/templates/goals/list.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="header">
  <div>
    <h1>Metas<span class="blink">▊</span></h1>
    <div class="subtitle">{{ goals | length }} meta(s) · inclui arquivadas</div>
  </div>
  <div class="actions">
    <a class="btn" href="/metas/nova">[ + ] nova meta</a>
  </div>
</div>

<div class="content">
  <div class="goals-grid">
    {% for g in goals %}
      {% set pct = progress_pct(g) %}
      <div class="goal-card {% if not g.active %}archived{% endif %}">
        <div class="goal-head">
          <h3>{{ g.title }}</h3>
          {% if g.target_date %}<span class="goal-date">até {{ g.target_date.strftime("%d/%m/%Y") }}</span>{% endif %}
        </div>
        <div class="goal-num">R$ {{ "%.2f" | format(g.saved_amount) | replace(".", ",") }}
          <span class="goal-of">/ R$ {{ "%.2f" | format(g.target_amount) | replace(".", ",") }}</span>
        </div>
        <div class="goal-bar"><div style="width: {{ pct | round(1) if pct < 100 else 100 }}%"></div></div>
        <div class="goal-pct">{{ pct | round(1) }}%</div>

        {% if g.active %}
        <form method="post" action="/metas/{{ g.id }}/progresso" style="display:flex; gap:6px; margin-top:10px;">
          <input type="text" name="amount" placeholder="+ valor poupado" style="flex:1; background: var(--bg); color: var(--text); border: 1px solid var(--border-2); padding: 6px 8px;">
          <button type="submit" class="btn secondary" style="padding: 6px 12px; font-size: 9px;">adicionar</button>
        </form>
        <form method="post" action="/metas/{{ g.id }}/archive" onsubmit="return confirm('Arquivar meta?')" style="margin-top:4px;">
          <button type="submit" class="btn secondary" style="padding: 4px 8px; font-size: 9px;">arquivar</button>
        </form>
        {% else %}
          <div style="margin-top: 10px;"><span class="pill">arquivada</span></div>
        {% endif %}
      </div>
    {% else %}
      <div class="empty" style="grid-column: 1/-1; text-align:center; padding: 40px; color: var(--dim);">Nenhuma meta cadastrada.</div>
    {% endfor %}
  </div>
</div>
{% endblock %}
```

- [ ] **Step 8.3.3: Criar `app/templates/goals/new.html`**

Arquivo: `app/templates/goals/new.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="header">
  <div>
    <h1>Nova meta<span class="blink">▊</span></h1>
    <div class="subtitle">defina um valor a poupar e um prazo opcional</div>
  </div>
  <div class="actions">
    <a class="btn secondary" href="/metas">[ ← ] voltar</a>
  </div>
</div>

<div class="content">
  <form method="post" action="/metas/nova" class="form-card">
    <div class="form-row">
      <label style="flex:1;">Título
        <input type="text" name="title" required maxlength="120" autofocus>
      </label>
    </div>
    <div class="form-row">
      <label>Valor alvo (R$)
        <input type="text" name="target_amount" placeholder="10000,00" required>
      </label>
      <label>Prazo (opcional)
        <input type="date" name="target_date">
      </label>
    </div>
    <div class="form-row">
      <label style="flex:1;">Nota
        <textarea name="note" rows="2" maxlength="400"></textarea>
      </label>
    </div>
    <div class="form-actions">
      <button type="submit" class="btn">[ criar meta ]</button>
    </div>
  </form>
</div>
{% endblock %}
```

- [ ] **Step 8.3.4: Anexar CSS de metas**

Anexar ao final de `app/static/css/app.css`:

```css
/* ========== METAS ========== */
.goals-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 14px; }
.goal-card { border: 1px solid var(--border); background: var(--bg-2); padding: 16px 18px; display: flex; flex-direction: column; gap: 8px; }
.goal-card.archived { opacity: 0.55; }
.goal-head { display: flex; justify-content: space-between; align-items: baseline; }
.goal-head h3 { font-size: 14px; font-weight: 500; color: var(--text); letter-spacing: 0; }
.goal-date { font-size: 10px; letter-spacing: 0.2em; color: var(--muted); text-transform: uppercase; }
.goal-num { font-size: 22px; color: var(--primary); font-variant-numeric: tabular-nums; font-weight: 500; margin-top: 4px; }
.goal-num .goal-of { font-size: 12px; color: var(--muted); }
.goal-bar { height: 6px; background: var(--bg-4); overflow: hidden; }
.goal-bar > div { height: 100%; background: linear-gradient(90deg, var(--primary-3), var(--primary)); box-shadow: 0 0 8px var(--primary-glow); }
.goal-pct { font-size: 11px; color: var(--muted); letter-spacing: 0.1em; align-self: flex-end; }
```

- [ ] **Step 8.3.5: Registrar em `app/main.py`**

```python
from app.routers import goals as goals_router
# ...
app.include_router(goals_router.router)
```

- [ ] **Step 8.3.6: Rebuild + testar**

```bash
docker compose up -d --build web
# /metas/nova → "Chile" 10000 até 31/12/2026
# /metas → adicionar 4000 → barra mostra 40%
```

- [ ] **Step 8.3.7: Commit e push**

```bash
git add app/routers/goals.py app/templates/goals/ app/static/css/app.css app/main.py
git commit -m "feat: página de metas com criação, progresso e arquivamento"
git push origin main
```

---

**Marco M8 alcançado:** metas de economia funcionais. Continua em M9.

---

## Milestone 9 — Relatórios históricos (gráficos)

### Task 9.1: Service de relatórios (TDD)

**Files:**
- Create: `app/services/reports.py`
- Create: `tests/services/test_reports_service.py`

- [ ] **Step 9.1.1: Escrever testes**

Arquivo: `tests/services/test_reports_service.py`

```python
from datetime import date
from decimal import Decimal

import pytest

from app.services import reports as svc
from app.services import transactions as tx_svc
from app.services.seed import seed_all


@pytest.fixture
def seeded(db):
    seed_all(db)
    return db


def _tx(**over):
    base = {
        "description": "x", "amount": Decimal("100"),
        "date": date(2026, 4, 15), "source_id": 1, "category_id": 2,
        "payment_mode": "debit", "type": "expense",
    }
    base.update(over)
    return base


def test_monthly_totals_returns_last_n_months(seeded):
    tx_svc.create(seeded, _tx(date=date(2026, 2, 10), amount=Decimal("1000")))
    tx_svc.create(seeded, _tx(date=date(2026, 3, 10), amount=Decimal("2000")))
    tx_svc.create(seeded, _tx(date=date(2026, 4, 10), amount=Decimal("3000")))
    rows = svc.monthly_totals(seeded, up_to=date(2026, 4, 30), months=3)
    assert len(rows) == 3
    assert rows[0]["year"] == 2026 and rows[0]["month"] == 2
    assert rows[0]["total_expense"] == Decimal("1000.00")
    assert rows[2]["total_expense"] == Decimal("3000.00")


def test_monthly_totals_fills_missing_months_with_zero(seeded):
    tx_svc.create(seeded, _tx(date=date(2026, 4, 10), amount=Decimal("500")))
    rows = svc.monthly_totals(seeded, up_to=date(2026, 4, 30), months=3)
    totals = [r["total_expense"] for r in rows]
    assert totals == [Decimal("0.00"), Decimal("0.00"), Decimal("500.00")]


def test_category_breakdown_by_month(seeded):
    tx_svc.create(seeded, _tx(category_id=1, date=date(2026, 3, 10),
                               amount=Decimal("1800")))
    tx_svc.create(seeded, _tx(category_id=2, date=date(2026, 3, 10),
                               amount=Decimal("500")))
    tx_svc.create(seeded, _tx(category_id=1, date=date(2026, 4, 10),
                               amount=Decimal("1800")))
    rows = svc.category_breakdown_by_month(
        seeded, up_to=date(2026, 4, 30), months=2
    )
    # Estrutura: {categoria_name: [valor_mes_1, valor_mes_2]}
    march_moradia = rows["Moradia"][0]
    april_moradia = rows["Moradia"][1]
    assert march_moradia == Decimal("1800.00")
    assert april_moradia == Decimal("1800.00")
    assert rows["Mercado"][0] == Decimal("500.00")
    assert rows["Mercado"][1] == Decimal("0.00")


def test_month_labels_returns_yyyy_mm(seeded):
    labels = svc.month_labels(date(2026, 4, 30), months=3)
    assert labels == ["2026-02", "2026-03", "2026-04"]
```

- [ ] **Step 9.1.2: Rodar — falham**

```bash
docker compose run --rm web pytest tests/services/test_reports_service.py -v
```

- [ ] **Step 9.1.3: Implementar service**

Arquivo: `app/services/reports.py`

```python
from calendar import monthrange
from datetime import date
from decimal import Decimal
from typing import TypedDict

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Category, Transaction


class MonthlyRow(TypedDict):
    year: int
    month: int
    total_expense: Decimal
    total_income: Decimal


def _iter_months_back(up_to: date, months: int) -> list[tuple[int, int]]:
    anchor_year = up_to.year
    anchor_month = up_to.month
    result: list[tuple[int, int]] = []
    for i in range(months - 1, -1, -1):
        idx = anchor_month - 1 - i
        y = anchor_year + idx // 12
        m = idx % 12 + 1
        result.append((y, m))
    return result


def month_labels(up_to: date, *, months: int) -> list[str]:
    return [f"{y}-{m:02d}" for y, m in _iter_months_back(up_to, months)]


def monthly_totals(
    db: Session, *, up_to: date, months: int = 6
) -> list[MonthlyRow]:
    periods = _iter_months_back(up_to, months)
    result: list[MonthlyRow] = []
    for y, m in periods:
        end_day = monthrange(y, m)[1]
        start, end = date(y, m, 1), date(y, m, end_day)
        rows = db.execute(
            select(
                Transaction.type,
                func.coalesce(func.sum(Transaction.amount), 0),
            )
            .where(Transaction.date >= start, Transaction.date <= end)
            .where(Transaction.status == "confirmed")
            .group_by(Transaction.type)
        ).all()
        expense = Decimal("0.00")
        income = Decimal("0.00")
        for t, total in rows:
            if t == "income":
                income = Decimal(total).quantize(Decimal("0.01"))
            else:
                expense = Decimal(total).quantize(Decimal("0.01"))
        result.append({
            "year": y, "month": m,
            "total_expense": expense, "total_income": income,
        })
    return result


def category_breakdown_by_month(
    db: Session, *, up_to: date, months: int = 6
) -> dict[str, list[Decimal]]:
    """Retorna dict[categoria_name] = [valor_mes_1, ..., valor_mes_N]."""
    periods = _iter_months_back(up_to, months)
    categories = db.query(Category).all()
    result = {cat.name: [Decimal("0.00")] * months for cat in categories}

    for idx, (y, m) in enumerate(periods):
        end_day = monthrange(y, m)[1]
        start, end = date(y, m, 1), date(y, m, end_day)
        rows = db.execute(
            select(Category.name, func.coalesce(func.sum(Transaction.amount), 0))
            .join(Transaction, Transaction.category_id == Category.id)
            .where(Transaction.date >= start, Transaction.date <= end)
            .where(Transaction.status == "confirmed", Transaction.type == "expense")
            .group_by(Category.name)
        ).all()
        for name, total in rows:
            result[name][idx] = Decimal(total).quantize(Decimal("0.01"))

    # Remover categorias sem nenhum valor
    return {k: v for k, v in result.items() if any(x > 0 for x in v)}
```

- [ ] **Step 9.1.4: Rodar testes → passam**

```bash
docker compose run --rm web pytest tests/services/test_reports_service.py -v
```

Expected: 4 testes PASS.

- [ ] **Step 9.1.5: Commit e push**

```bash
git add app/services/reports.py tests/services/test_reports_service.py
git commit -m "feat: service de relatórios (totais mensais + breakdown por categoria)"
git push origin main
```

---

### Task 9.2: Router e template de `/relatorios` com Chart.js

**Files:**
- Create: `app/routers/reports.py`
- Create: `app/templates/reports/index.html`
- Modify: `app/main.py`

- [ ] **Step 9.2.1: Criar `app/routers/reports.py`**

Arquivo: `app/routers/reports.py`

```python
import json
from datetime import date
from decimal import Decimal
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.deps import get_db
from app.services import reports as svc

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/relatorios", tags=["reports"])


def _decimal_list(values: list[Decimal]) -> list[float]:
    return [float(v) for v in values]


@router.get("", response_class=HTMLResponse)
def reports_view(
    request: Request,
    db: Session = Depends(get_db),
    months: int = 6,
) -> HTMLResponse:
    months = max(3, min(months, 24))
    today = date.today()
    labels = svc.month_labels(today, months=months)
    totals = svc.monthly_totals(db, up_to=today, months=months)
    breakdown = svc.category_breakdown_by_month(db, up_to=today, months=months)

    # Dados serializados para o Chart.js
    chart_totals = {
        "labels": labels,
        "expense": [float(row["total_expense"]) for row in totals],
        "income": [float(row["total_income"]) for row in totals],
    }
    chart_breakdown = {
        "labels": labels,
        "datasets": [
            {"label": cat, "data": _decimal_list(vals)}
            for cat, vals in breakdown.items()
        ],
    }

    return templates.TemplateResponse(
        request, "reports/index.html",
        {
            "active_nav": "reports",
            "page_title": "Relatórios",
            "months": months,
            "chart_totals_json": json.dumps(chart_totals),
            "chart_breakdown_json": json.dumps(chart_breakdown),
        },
    )
```

- [ ] **Step 9.2.2: Criar `app/templates/reports/index.html`**

Arquivo: `app/templates/reports/index.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="header">
  <div>
    <h1>Relatórios<span class="blink">▊</span></h1>
    <div class="subtitle">últimos {{ months }} meses</div>
  </div>
  <div class="actions">
    <form method="get" action="/relatorios" style="display:flex; gap:6px; align-items:center;">
      <select name="months" onchange="this.form.submit()" style="background: var(--bg); color: var(--text); border: 1px solid var(--border-2); padding: 6px 10px;">
        <option value="3"  {% if months == 3 %}selected{% endif %}>3 meses</option>
        <option value="6"  {% if months == 6 %}selected{% endif %}>6 meses</option>
        <option value="12" {% if months == 12 %}selected{% endif %}>12 meses</option>
        <option value="24" {% if months == 24 %}selected{% endif %}>24 meses</option>
      </select>
    </form>
  </div>
</div>

<div class="content">
  <div class="pnl">
    <div class="pnl-h"><span>evolução mensal</span><span class="tag">total</span></div>
    <div class="pnl-b" style="padding: 16px;">
      <canvas id="chart-totals" height="90"></canvas>
    </div>
  </div>

  <div class="pnl">
    <div class="pnl-h"><span>por categoria</span><span class="tag">barras empilhadas</span></div>
    <div class="pnl-b" style="padding: 16px;">
      <canvas id="chart-breakdown" height="110"></canvas>
    </div>
  </div>
</div>
{% endblock %}

{% block scripts %}
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.6"></script>
<script>
const totals = {{ chart_totals_json | safe }};
const breakdown = {{ chart_breakdown_json | safe }};

const textColor = "#D8D4C8";
const muted = "#8B8F99";
const primary = "#C084FC";
const ok = "#4AC776";

Chart.defaults.color = muted;
Chart.defaults.font.family = "JetBrains Mono, monospace";
Chart.defaults.font.size = 11;

new Chart(document.getElementById("chart-totals"), {
  type: "line",
  data: {
    labels: totals.labels,
    datasets: [
      {
        label: "Gastos",
        data: totals.expense,
        borderColor: primary,
        backgroundColor: "rgba(192,132,252,0.15)",
        fill: true,
        tension: 0.3,
      },
      {
        label: "Receitas",
        data: totals.income,
        borderColor: ok,
        backgroundColor: "rgba(74,199,118,0.1)",
        fill: false,
        tension: 0.3,
      },
    ],
  },
  options: {
    responsive: true,
    plugins: { legend: { labels: { color: textColor } } },
    scales: {
      x: { grid: { color: "rgba(255,255,255,0.05)" } },
      y: { grid: { color: "rgba(255,255,255,0.05)" } },
    },
  },
});

const palette = ["#C084FC", "#4AC776", "#FFB74A", "#FF8B6B", "#88C0D0", "#BF616A",
                 "#A855F7", "#EBCB8B", "#D08770", "#81A1C1", "#A3BE8C", "#B48EAD"];
breakdown.datasets.forEach((ds, i) => {
  ds.backgroundColor = palette[i % palette.length];
  ds.borderWidth = 0;
});

new Chart(document.getElementById("chart-breakdown"), {
  type: "bar",
  data: breakdown,
  options: {
    responsive: true,
    plugins: { legend: { labels: { color: textColor } } },
    scales: {
      x: { stacked: true, grid: { color: "rgba(255,255,255,0.05)" } },
      y: { stacked: true, grid: { color: "rgba(255,255,255,0.05)" } },
    },
  },
});
</script>
{% endblock %}
```

- [ ] **Step 9.2.3: Registrar router em `app/main.py`**

```python
from app.routers import reports as reports_router
# ...
app.include_router(reports_router.router)
```

- [ ] **Step 9.2.4: Rebuild + testar**

```bash
docker compose up -d --build web
# /relatorios → dois gráficos (linha de totais + barras empilhadas por categoria)
```

- [ ] **Step 9.2.5: Commit e push**

```bash
git add app/routers/reports.py app/templates/reports/ app/main.py
git commit -m "feat: página de relatórios com gráficos Chart.js (totais + breakdown)"
git push origin main
```

---

**Marco M9 alcançado:** relatórios históricos com gráficos. Continua em M10.

---

## Milestone 10 — Projeção futura

### Task 10.1: Service de projeção (TDD)

**Files:**
- Create: `app/services/projection.py`
- Create: `tests/services/test_projection_service.py`

- [ ] **Step 10.1.1: Escrever testes**

Arquivo: `tests/services/test_projection_service.py`

```python
from datetime import date
from decimal import Decimal

import pytest

from app.models import FixedRule, Source
from app.services import installments as inst_svc
from app.services import projection as svc
from app.services.seed import seed_all


@pytest.fixture
def seeded(db):
    seed_all(db)
    return db


def _principal(db):
    return db.query(Source).filter_by(slug="conta-principal").first()


def test_monthly_projection_aggregates_installments(seeded):
    src = _principal(seeded)
    inst_svc.create_plan(seeded, {
        "description": "iPhone", "installments_count": 12,
        "first_purchase_date": date(2026, 4, 3),
        "source_id": src.id, "category_id": 1,
        "input_mode": "total", "total_amount": Decimal("6240.00"),
    })
    # projeção para maio: primeira parcela (vence 10/mai = 520)
    rows = svc.project_months(seeded, start=date(2026, 5, 1), months=3)
    may = next(r for r in rows if r["year"] == 2026 and r["month"] == 5)
    assert may["installments_total"] == Decimal("520.00")


def test_monthly_projection_includes_fixed_rules(seeded):
    src = _principal(seeded)
    rule = FixedRule(
        description="Aluguel", expected_amount=Decimal("1800.00"),
        recurrence="monthly", day_of_month=5,
        source_id=src.id, category_id=1,
        payment_mode="debit", type="expense",
        active_from=date(2026, 1, 1),
    )
    seeded.add(rule)
    seeded.commit()
    rows = svc.project_months(seeded, start=date(2026, 5, 1), months=3)
    may = next(r for r in rows if r["month"] == 5)
    assert may["fixed_total"] == Decimal("1800.00")


def test_monthly_projection_computes_grand_total(seeded):
    src = _principal(seeded)
    inst_svc.create_plan(seeded, {
        "description": "Sofá", "installments_count": 3,
        "first_purchase_date": date(2026, 4, 3),
        "source_id": src.id, "category_id": 1,
        "input_mode": "total", "total_amount": Decimal("900.00"),
    })
    rule = FixedRule(
        description="Aluguel", expected_amount=Decimal("1800.00"),
        recurrence="monthly", day_of_month=5,
        source_id=src.id, category_id=1,
        payment_mode="debit", type="expense",
        active_from=date(2026, 1, 1),
    )
    seeded.add(rule)
    seeded.commit()
    rows = svc.project_months(seeded, start=date(2026, 5, 1), months=2)
    may = next(r for r in rows if r["month"] == 5)
    # Fixos 1800 + parcela Sofá 300 = 2100
    assert may["grand_total"] == Decimal("2100.00")


def test_ledger_for_month_lists_all_obligations_sorted(seeded):
    src = _principal(seeded)
    rule = FixedRule(
        description="Aluguel", expected_amount=Decimal("1800.00"),
        recurrence="monthly", day_of_month=5,
        source_id=src.id, category_id=1,
        payment_mode="debit", type="expense",
        active_from=date(2026, 1, 1),
    )
    seeded.add(rule)
    seeded.commit()
    inst_svc.create_plan(seeded, {
        "description": "iPhone", "installments_count": 12,
        "first_purchase_date": date(2026, 4, 3),
        "source_id": src.id, "category_id": 1,
        "input_mode": "total", "total_amount": Decimal("6240.00"),
    })
    rows = svc.ledger_for_month(seeded, year=2026, month=5)
    # Deve conter Aluguel 05/05 + iPhone parc2 10/05
    descs = [r["description"] for r in rows]
    assert any("Aluguel" in d for d in descs)
    assert any("iPhone" in d for d in descs)
    # Ordenado por data
    dates = [r["date"] for r in rows]
    assert dates == sorted(dates)
```

- [ ] **Step 10.1.2: Rodar — falham**

```bash
docker compose run --rm web pytest tests/services/test_projection_service.py -v
```

- [ ] **Step 10.1.3: Implementar service**

Arquivo: `app/services/projection.py`

```python
from calendar import monthrange
from datetime import date
from decimal import Decimal
from typing import Any, TypedDict

from sqlalchemy.orm import Session

from app.models import FixedRule, Transaction
from app.services.fixed_projection import project_rule


class MonthSummary(TypedDict):
    year: int
    month: int
    fixed_total: Decimal
    installments_total: Decimal
    grand_total: Decimal


def _month_bounds(year: int, month: int) -> tuple[date, date]:
    return date(year, month, 1), date(year, month, monthrange(year, month)[1])


def _iter_months(start: date, months: int) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    y, m = start.year, start.month
    for _ in range(months):
        result.append((y, m))
        m += 1
        if m > 12:
            m = 1
            y += 1
    return result


def project_months(
    db: Session, *, start: date, months: int
) -> list[MonthSummary]:
    periods = _iter_months(start, months)
    rules = db.query(FixedRule).filter(FixedRule.archived.is_(False)).all()
    result: list[MonthSummary] = []

    for y, m in periods:
        month_start, month_end = _month_bounds(y, m)

        # Fixos projetados on-demand
        fixed_total = Decimal("0.00")
        for rule in rules:
            occs = project_rule(rule, start=month_start, end=month_end)
            fixed_total += rule.expected_amount * len(occs)
        fixed_total = fixed_total.quantize(Decimal("0.01"))

        # Parcelas projetadas (já materializadas como Transaction)
        inst_total_q = db.query(
            Transaction.amount
        ).filter(
            Transaction.origin == "installment",
            Transaction.date >= month_start,
            Transaction.date <= month_end,
        ).all()
        inst_total = sum((row.amount for row in inst_total_q), Decimal("0.00")).quantize(
            Decimal("0.01")
        )

        result.append({
            "year": y, "month": m,
            "fixed_total": fixed_total,
            "installments_total": inst_total,
            "grand_total": (fixed_total + inst_total).quantize(Decimal("0.01")),
        })

    return result


def ledger_for_month(db: Session, *, year: int, month: int) -> list[dict[str, Any]]:
    """Lista ordenada por data de todas as obrigações previstas para o mês:
    fixos (da regra) + parcelas (lançamentos projetados) + lançamentos confirmados.
    """
    start, end = _month_bounds(year, month)
    result: list[dict[str, Any]] = []

    rules = db.query(FixedRule).filter(FixedRule.archived.is_(False)).all()
    for rule in rules:
        for occ in project_rule(rule, start=start, end=end):
            result.append({
                "kind": "fixed",
                "description": rule.description,
                "date": occ,
                "amount": rule.expected_amount,
                "source": rule.source.name,
                "category": rule.category.name,
                "ref_id": rule.id,
            })

    installments = (
        db.query(Transaction)
        .filter(
            Transaction.origin == "installment",
            Transaction.date >= start, Transaction.date <= end,
        )
        .all()
    )
    for tx in installments:
        result.append({
            "kind": "installment",
            "description": tx.description,
            "date": tx.date,
            "amount": tx.amount,
            "source": tx.source.name,
            "category": tx.category.name,
            "ref_id": tx.id,
        })

    result.sort(key=lambda r: (r["date"], r["kind"]))
    return result
```

- [ ] **Step 10.1.4: Rodar testes → passam**

```bash
docker compose run --rm web pytest tests/services/test_projection_service.py -v
```

Expected: 4 testes PASS.

- [ ] **Step 10.1.5: Commit e push**

```bash
git add app/services/projection.py tests/services/test_projection_service.py
git commit -m "feat: service de projeção com ledger e totais mensais (fixos + parcelas)"
git push origin main
```

---

### Task 10.2: Página `/projecao` com ledger do próximo mês + sparkline

**Files:**
- Create: `app/routers/projection.py`
- Create: `app/templates/projection/index.html`
- Modify: `app/main.py`

- [ ] **Step 10.2.1: Criar `app/routers/projection.py`**

Arquivo: `app/routers/projection.py`

```python
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
```

- [ ] **Step 10.2.2: Criar `app/templates/projection/index.html`**

Arquivo: `app/templates/projection/index.html`

```html
{% extends "base.html" %}

{% block content %}
<div class="header">
  <div>
    <h1>Projeção<span class="blink">▊</span></h1>
    <div class="subtitle">próximos {{ months }} meses · ledger de {{ "%02d" | format(target_month) }}/{{ target_year }}</div>
  </div>
  <div class="actions">
    <form method="get" action="/projecao" style="display:flex; gap:6px;">
      <select name="months" onchange="this.form.submit()" style="background: var(--bg); color: var(--text); border: 1px solid var(--border-2); padding: 6px 10px;">
        <option value="3"  {% if months == 3 %}selected{% endif %}>3 meses</option>
        <option value="6"  {% if months == 6 %}selected{% endif %}>6 meses</option>
        <option value="12" {% if months == 12 %}selected{% endif %}>12 meses</option>
      </select>
    </form>
  </div>
</div>

<div class="content">
  <div class="pnl">
    <div class="pnl-h"><span>evolução previsto</span><span class="tag">fixos + parcelas</span></div>
    <div class="pnl-b" style="padding: 16px;">
      <canvas id="chart-proj" height="80"></canvas>
    </div>
  </div>

  <div class="pnl">
    <div class="pnl-h">
      <span>ledger · {{ "%02d" | format(target_month) }}/{{ target_year }}</span>
      <span class="tag">total R$ {{ "%.2f" | format(ledger_total) | replace(".", ",") }}</span>
    </div>
    <div class="pnl-b">
      <table class="tx-table" style="margin:0; border: none;">
        <thead>
          <tr><th>Data</th><th>Descrição</th><th>Tipo</th><th>Fonte</th><th>Valor</th></tr>
        </thead>
        <tbody>
          {% for r in ledger %}
            <tr>
              <td>{{ r.date.strftime("%d/%m") }}</td>
              <td>{{ r.description }}</td>
              <td>
                {% if r.kind == "fixed" %}<span class="pill mode-pix">fixo</span>
                {% else %}<span class="pill mode-credit">parcela</span>{% endif %}
              </td>
              <td>{{ r.source }}</td>
              <td class="num">R$ {{ "%.2f" | format(r.amount) | replace(".", ",") }}</td>
            </tr>
          {% else %}
            <tr><td colspan="5" class="empty">Sem obrigações previstas neste mês.</td></tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
</div>
{% endblock %}

{% block scripts %}
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.6"></script>
<script>
const proj = {{ chart_json | safe }};
Chart.defaults.color = "#8B8F99";
Chart.defaults.font.family = "JetBrains Mono, monospace";

new Chart(document.getElementById("chart-proj"), {
  type: "bar",
  data: {
    labels: proj.labels,
    datasets: [
      { label: "Fixos", data: proj.fixed, backgroundColor: "#4AC776" },
      { label: "Parcelas", data: proj.installments, backgroundColor: "#C084FC" },
    ],
  },
  options: {
    responsive: true,
    plugins: { legend: { labels: { color: "#D8D4C8" } } },
    scales: {
      x: { stacked: true, grid: { color: "rgba(255,255,255,0.05)" } },
      y: { stacked: true, grid: { color: "rgba(255,255,255,0.05)" } },
    },
  },
});
</script>
{% endblock %}
```

- [ ] **Step 10.2.3: Registrar em `app/main.py`**

```python
from app.routers import projection as projection_router
# ...
app.include_router(projection_router.router)
```

- [ ] **Step 10.2.4: Rebuild + testar**

```bash
docker compose up -d --build web
# /projecao → barras empilhadas (fixos + parcelas) + ledger do próximo mês
```

- [ ] **Step 10.2.5: Commit e push**

```bash
git add app/routers/projection.py app/templates/projection/ app/main.py
git commit -m "feat: página de projeção com sparkline de N meses e ledger do próximo mês"
git push origin main
```

---

**Marco M10 alcançado:** projeção futura com gráfico + ledger detalhado. Continua em M11.

---

## Milestone 11 — Polimento de responsividade

Esta etapa revisa todas as páginas em três viewports (desktop ≥1200, tablet 768-1199, mobile <768) e ajusta pontos que ficaram ruins. Não introduz funcionalidade nova — só refina CSS.

### Task 11.1: Audit e ajustes mobile nas páginas de lista (transactions, installments, fixed)

**Files:**
- Modify: `app/static/css/app.css`
- Modify: `app/templates/transactions/_row.html` (data-labels para mobile cards)

- [ ] **Step 11.1.1: Adicionar `data-label` em `_row.html` de transactions**

Arquivo: `app/templates/transactions/_row.html`

```html
<tr>
  <td data-label="Data">{{ tx.date.strftime("%d/%m") }}</td>
  <td data-label="Descrição"><a href="/lancamentos/{{ tx.id }}/editar" style="color:var(--text);">{{ tx.description }}</a></td>
  <td data-label="Categoria">{{ tx.category.name }}</td>
  <td data-label="Fonte">{{ tx.source.name }}</td>
  <td data-label="Modo"><span class="pill mode-{{ tx.payment_mode }}">{{ tx.payment_mode }}</span></td>
  <td data-label="Devido em" class="due">
    {% set due = tx.compute_due_date(tx.source) %}
    {% if due != tx.date %}<span class="due-shift">→ {{ due.strftime("%d/%m") }}</span>
    {% else %}<span class="dim">—</span>{% endif %}
  </td>
  <td data-label="Valor" class="num">R$ {{ "%.2f" | format(tx.amount) | replace(".", ",") }}</td>
  <td data-label="Ações">
    <form method="post" action="/lancamentos/{{ tx.id }}/delete" onsubmit="return confirm('Apagar este lançamento?')" style="display:inline;">
      <button type="submit" class="btn danger" style="padding:4px 8px; font-size:9px;">×</button>
    </form>
  </td>
</tr>
```

- [ ] **Step 11.1.2: Ajustar CSS mobile para tabelas virarem cards**

Anexar ao final de `app/static/css/app.css` (substituindo a regra mobile antiga de `.tx-table` se houver):

```css
/* Mobile: tabelas viram cards empilhados */
@media (max-width: 767px) {
  .tx-table, .tx-table thead, .tx-table tbody, .tx-table tr, .tx-table td, .tx-table th { display: block; }
  .tx-table thead { position: absolute; left: -9999px; }
  .tx-table tr {
    border: 1px solid var(--border); background: var(--bg-2);
    margin-bottom: 10px; padding: 10px 12px;
  }
  .tx-table td {
    border: none; padding: 4px 0;
    display: grid; grid-template-columns: 90px 1fr; gap: 8px; align-items: baseline;
  }
  .tx-table td::before {
    content: attr(data-label);
    font-size: 9px; letter-spacing: 0.2em; color: var(--muted); text-transform: uppercase;
  }
  .tx-table td.num { text-align: left; }
  .tx-table td.empty { grid-template-columns: 1fr; text-align: center; padding: 20px 0; }
  .tx-table td.empty::before { display: none; }
}
```

- [ ] **Step 11.1.3: Aplicar o mesmo padrão nos demais `list.html` (installments, fixed, projection)**

Percorrer os arquivos `app/templates/installments/list.html`, `installments/detail.html`, `fixed/list.html`, `projection/index.html` (tabela do ledger) e adicionar `data-label="..."` em cada `<td>` conforme o `<th>` correspondente. Exemplo para `fixed/list.html` na tabela de ocorrências:

```html
<td data-label="Data">{{ o.date.strftime("%d/%m") }}</td>
<td data-label="Descrição">{{ o.description }}</td>
<td data-label="Esperado" class="num">R$ {{ "%.2f" | format(o.expected_amount) | replace(".", ",") }}</td>
<!-- etc. -->
```

- [ ] **Step 11.1.4: Testar em mobile emulado (DevTools, 375px)**

```bash
docker compose up -d --build web
# DevTools → responsive mode → 375×667
# Navegar /lancamentos, /parcelados, /fixos, /projecao — tabelas viram cards legíveis
```

- [ ] **Step 11.1.5: Commit e push**

```bash
git add app/static/css/app.css app/templates/
git commit -m "style: tabelas viram cards empilhados em mobile via data-label"
git push origin main
```

---

### Task 11.2: Revisão do hero e metrics do dashboard em mobile

**Files:**
- Modify: `app/static/css/app.css`

- [ ] **Step 11.2.1: Ajustar `.hero` e `.hero .metrics` em mobile**

Substituir/adicionar a seção mobile do hero em `app/static/css/app.css`:

```css
@media (max-width: 767px) {
  .hero { grid-template-columns: 1fr; gap: 16px; padding: 14px; }
  .hero::before { display: none; }
  .hero .hero-num { font-size: 34px; }
  .hero .prog-lbl { flex-direction: column; gap: 4px; align-items: flex-start; }
  .hero .metrics { grid-template-columns: 1fr 1fr; gap: 8px 12px; }
  .hero .m { padding-left: 8px; }
  .hero .m .val { font-size: 14px; }

  .grid-3 { grid-template-columns: 1fr; gap: 12px; }
  .pnl-b { padding: 8px 12px 12px; }
  .line { font-size: 13px; gap: 10px; padding: 10px 0; }
  .line .vl { font-size: 13px; min-width: auto; }
  .line .pct { display: none; }

  .header { flex-direction: column; align-items: stretch; gap: 12px; padding: 14px 12px; }
  .header h1 { font-size: 22px; }
  .header .actions { flex-wrap: wrap; }
}
```

- [ ] **Step 11.2.2: Testar**

```bash
docker compose up -d --build web
# /  em 375px → hero compacto, metrics em grid 2x2, grid-3 empilhado, escondendo %
```

- [ ] **Step 11.2.3: Commit e push**

```bash
git add app/static/css/app.css
git commit -m "style: dashboard em mobile com hero compacto e metrics 2x2"
git push origin main
```

---

### Task 11.3: Menu hamburger + drawer de sidebar em mobile

**Files:**
- Modify: `app/static/css/app.css`
- Modify: `app/static/js/app.js`
- Modify: `app/templates/_partials/topbar.html`
- Modify: `app/templates/base.html`

- [ ] **Step 11.3.1: Garantir que o hamburger só aparece em mobile e fecha ao clicar no link**

Atualizar `app/static/js/app.js`:

```javascript
document.addEventListener("DOMContentLoaded", () => {
  const btn = document.querySelector(".hamburger");
  const backdrop = document.querySelector(".side-backdrop");
  const sidebarLinks = document.querySelectorAll(".side .nav a");

  const close = () => document.body.classList.remove("side-open");
  if (btn) btn.addEventListener("click", () => document.body.classList.toggle("side-open"));
  if (backdrop) backdrop.addEventListener("click", close);
  sidebarLinks.forEach(link => link.addEventListener("click", close));

  // Fechar com ESC
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") close();
  });
});
```

- [ ] **Step 11.3.2: Ajustar CSS do drawer para animar corretamente**

Garantir em `app/static/css/app.css` (substituir a seção `@media (max-width: 767px)` da sidebar):

```css
@media (max-width: 767px) {
  .app { grid-template-columns: 1fr; }
  .side {
    position: fixed; left: 0; top: 0; bottom: 0; width: 280px;
    z-index: 60; transform: translateX(-100%);
    transition: transform 0.24s cubic-bezier(0.4, 0.0, 0.2, 1);
    padding: 20px 18px;
    box-shadow: 4px 0 20px rgba(0,0,0,0.5);
  }
  body.side-open .side { transform: translateX(0); }
  body.side-open .side-backdrop {
    display: block; animation: fadeIn 0.2s;
  }
  @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
  .hamburger { display: block; }
}
```

- [ ] **Step 11.3.3: Testar toggle, backdrop, ESC, link-click**

```bash
docker compose up -d --build web
# mobile 375px → clicar hamburger abre drawer, backdrop aparece, clique em link fecha, ESC fecha
```

- [ ] **Step 11.3.4: Commit e push**

```bash
git add app/static/js/app.js app/static/css/app.css
git commit -m "style: drawer da sidebar em mobile com animação e fechamento por ESC/link/backdrop"
git push origin main
```

---

### Task 11.4: Ajustes nos formulários em mobile (novo lançamento, novo parcelamento, novo fixo, metas)

**Files:**
- Modify: `app/static/css/app.css`

- [ ] **Step 11.4.1: Formulários em coluna única em mobile com min-width 100%**

Garantir em `app/static/css/app.css`:

```css
@media (max-width: 767px) {
  .form-card { padding: 14px; max-width: 100%; }
  .form-row { flex-direction: column; gap: 10px; margin-bottom: 10px; }
  .form-row label { min-width: 0; width: 100%; }
  .form-row input, .form-row select, .form-row textarea { width: 100%; font-size: 14px; padding: 10px; }
  .form-actions { flex-direction: column; }
  .form-actions .btn { width: 100%; text-align: center; }
  .filters { flex-direction: column; align-items: stretch; gap: 8px; padding: 10px; }
  .filters label { width: 100%; }
  .filters input, .filters select { width: 100%; min-width: 0; }
}
```

- [ ] **Step 11.4.2: Testar todos os formulários em 375px**

```bash
docker compose up -d --build web
# testar: /lancamentos/novo, /parcelados/novo, /fixos/novo, /metas/nova, /config/sistema
```

- [ ] **Step 11.4.3: Commit e push**

```bash
git add app/static/css/app.css
git commit -m "style: formulários em coluna única ocupando largura total em mobile"
git push origin main
```

---

### Task 11.5: Cards de metas e charts em mobile

**Files:**
- Modify: `app/static/css/app.css`

- [ ] **Step 11.5.1: Ajustes finais**

Anexar ao final de `app/static/css/app.css`:

```css
@media (max-width: 767px) {
  .goals-grid { grid-template-columns: 1fr; }
  .goal-card { padding: 14px; }
  .goal-num { font-size: 18px; }
  /* Charts ajustam automaticamente (Chart.js responsive:true) */
}

/* Scrollbar estilizada (só em desktop para consistência) */
@media (min-width: 768px) {
  ::-webkit-scrollbar { width: 10px; height: 10px; }
  ::-webkit-scrollbar-track { background: var(--bg); }
  ::-webkit-scrollbar-thumb { background: var(--border-2); border: 2px solid var(--bg); }
  ::-webkit-scrollbar-thumb:hover { background: var(--muted); }
}

/* Acessibilidade: reduzir motion se preferido */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
  .hero .hero-num::after, .header .blink, .topbar .pulse { animation: none; }
}
```

- [ ] **Step 11.5.2: Testar tudo no DevTools responsive em 3 viewports**

```bash
docker compose up -d --build web
# 1440px · 900px · 375px — passar por todas as páginas e confirmar que nada quebra
```

- [ ] **Step 11.5.3: Commit e push**

```bash
git add app/static/css/app.css
git commit -m "style: metas em mobile, scrollbar custom desktop, reduced-motion support"
git push origin main
```

---

**Marco M11 alcançado:** UI completamente responsiva em desktop/tablet/mobile. Continua em M12.

---

## Milestone 12 — Scripts de operação (update/backup/restore)

### Task 12.1: `scripts/backup.sh` com rotação

**Files:**
- Create: `scripts/backup.sh`

- [ ] **Step 12.1.1: Criar `scripts/backup.sh`**

Arquivo: `scripts/backup.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

# scripts/backup.sh — dump do Postgres em backups/ com rotação.
# Uso: ./scripts/backup.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

BACKUP_DIR="$ROOT_DIR/backups"
RETENTION=${BACKUP_RETENTION:-14}

if [ ! -f .env ]; then
  echo "ERRO: .env não encontrado em $ROOT_DIR" >&2
  exit 1
fi

# Carrega variáveis do .env
set -a
# shellcheck disable=SC1091
source .env
set +a

: "${POSTGRES_USER:?POSTGRES_USER não definido em .env}"
: "${POSTGRES_DB:?POSTGRES_DB não definido em .env}"

mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +"%Y-%m-%d_%H%M%S")
OUTFILE="$BACKUP_DIR/finance_${TIMESTAMP}.sql.gz"

echo "▸ Gerando backup: $OUTFILE"
docker compose exec -T db pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists \
  | gzip > "$OUTFILE"

SIZE=$(du -h "$OUTFILE" | cut -f1)
echo "✓ Backup concluído: $OUTFILE ($SIZE)"

# Rotação: remove os mais antigos além de $RETENTION
COUNT=$(ls -1 "$BACKUP_DIR"/finance_*.sql.gz 2>/dev/null | wc -l)
if [ "$COUNT" -gt "$RETENTION" ]; then
  TO_REMOVE=$((COUNT - RETENTION))
  echo "▸ Rotação: removendo $TO_REMOVE backup(s) antigo(s) (retenção=$RETENTION)"
  # shellcheck disable=SC2012
  ls -1t "$BACKUP_DIR"/finance_*.sql.gz | tail -n "$TO_REMOVE" | xargs -r rm -v
fi

echo "▸ Backups atuais:"
ls -lh "$BACKUP_DIR"/finance_*.sql.gz 2>/dev/null || true
```

- [ ] **Step 12.1.2: Dar permissão de execução**

```bash
chmod +x scripts/backup.sh
```

- [ ] **Step 12.1.3: Executar e verificar**

```bash
./scripts/backup.sh
ls -lh backups/
```

Expected: arquivo `.sql.gz` em `backups/` com timestamp atual.

- [ ] **Step 12.1.4: Commit e push**

```bash
git add scripts/backup.sh
git commit -m "infra: script backup.sh com dump SQL e rotação configurável (padrão 14)"
git push origin main
```

---

### Task 12.2: `scripts/restore.sh` com confirmação explícita

**Files:**
- Create: `scripts/restore.sh`

- [ ] **Step 12.2.1: Criar `scripts/restore.sh`**

Arquivo: `scripts/restore.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

# scripts/restore.sh — restaura dump do Postgres.
# Uso: ./scripts/restore.sh backups/finance_YYYY-MM-DD_HHMMSS.sql.gz

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

if [ $# -ne 1 ]; then
  echo "Uso: $0 <arquivo.sql.gz>" >&2
  exit 1
fi

DUMP_FILE="$1"
if [ ! -f "$DUMP_FILE" ]; then
  echo "ERRO: arquivo não encontrado: $DUMP_FILE" >&2
  exit 1
fi

if [ ! -f .env ]; then
  echo "ERRO: .env não encontrado em $ROOT_DIR" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1091
source .env
set +a

: "${POSTGRES_USER:?POSTGRES_USER não definido em .env}"
: "${POSTGRES_DB:?POSTGRES_DB não definido em .env}"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                       ATENÇÃO                            ║"
echo "║                                                          ║"
echo "║  Esta operação vai APAGAR todos os dados atuais do       ║"
echo "║  banco '$POSTGRES_DB' e substituí-los pelo conteúdo de:  "
echo "║  $DUMP_FILE"
echo "║                                                          ║"
echo "║  Esta ação NÃO PODE ser desfeita sem outro backup.       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
read -r -p "Digite 'yes' (minúsculas) para confirmar: " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
  echo "Cancelado."
  exit 0
fi

echo "▸ Parando container web..."
docker compose stop web

echo "▸ Restaurando dump..."
gunzip -c "$DUMP_FILE" \
  | docker compose exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1

echo "▸ Subindo web novamente..."
docker compose up -d web

echo "✓ Restauração concluída."
```

- [ ] **Step 12.2.2: Permissão de execução**

```bash
chmod +x scripts/restore.sh
```

- [ ] **Step 12.2.3: Testar restauração em um backup local**

```bash
./scripts/restore.sh backups/finance_<timestamp>.sql.gz
# digitar "yes" quando solicitado; ao final, validar que /lancamentos lista os dados
```

- [ ] **Step 12.2.4: Commit e push**

```bash
git add scripts/restore.sh
git commit -m "infra: script restore.sh com confirmação explícita e stop do web"
git push origin main
```

---

### Task 12.3: `scripts/update.sh` com backup automático prévio

**Files:**
- Create: `scripts/update.sh`

- [ ] **Step 12.3.1: Criar `scripts/update.sh`**

Arquivo: `scripts/update.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

# scripts/update.sh — atualiza a aplicação.
# Faz: backup → git pull → rebuild → up -d → alembic upgrade head

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

echo "═════════════════════════════════════════"
echo " MyFinanceApp · update $(date +'%Y-%m-%d %H:%M:%S')"
echo "═════════════════════════════════════════"
echo ""

# 1. Checa se há containers rodando
if ! docker compose ps --quiet db | grep -q .; then
  echo "AVISO: container db não está rodando — pulando backup."
  SKIP_BACKUP=1
else
  SKIP_BACKUP=0
fi

# 2. Backup automático
if [ "$SKIP_BACKUP" -eq 0 ]; then
  echo "▸ [1/5] Backup automático pré-update"
  "$SCRIPT_DIR/backup.sh"
  echo ""
fi

# 3. git pull
echo "▸ [2/5] git pull origin main"
git fetch origin
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)
if [ "$LOCAL" = "$REMOTE" ]; then
  echo "  (já atualizado)"
else
  git pull --ff-only origin main
fi
echo ""

# 4. Rebuild
echo "▸ [3/5] docker compose build"
docker compose build
echo ""

# 5. Up
echo "▸ [4/5] docker compose up -d"
docker compose up -d
echo ""

# 6. Aguarda db healthy
echo "▸ aguardando Postgres ficar pronto..."
for _ in $(seq 1 30); do
  if docker compose exec -T db pg_isready -U "${POSTGRES_USER:-finance}" -d "${POSTGRES_DB:-finance}" >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

# 7. Alembic upgrade
echo "▸ [5/5] alembic upgrade head"
docker compose exec -T web alembic upgrade head
echo ""

# 8. Status final
echo "═════════════════════════════════════════"
echo "✓ Update concluído"
echo "═════════════════════════════════════════"
docker compose ps
```

- [ ] **Step 12.3.2: Permissão de execução**

```bash
chmod +x scripts/update.sh
```

- [ ] **Step 12.3.3: Testar**

```bash
./scripts/update.sh
# deve rodar backup → git pull → build → up → migrations
```

- [ ] **Step 12.3.4: Commit e push**

```bash
git add scripts/update.sh
git commit -m "infra: script update.sh com backup automático antes de atualizar"
git push origin main
```

---

### Task 12.4: README final com instruções completas

**Files:**
- Modify: `README.md`

- [ ] **Step 12.4.1: Atualizar `README.md` com versão completa**

Arquivo: `README.md`

````markdown
# MyFinanceApp

Sistema pessoal de finanças — dashboard mensal com ciclo de fatura de cartão de crédito, gastos fixos recorrentes, parcelamentos, metas e projeções futuras. Executa em Docker no servidor caseiro.

Projeto monousuário, sem login, desenhado para uso em rede local.

## Screenshot

![Dashboard](docs/screenshots/dashboard.png)

_(screenshot adicionada após primeiro deploy)_

## Recursos

- **Dashboard** mensal com gasto acumulado, alvo de orçamento, receita, saldo previsto e alertas.
- **Lançamentos** avulsos (crédito / débito / PIX) com filtros por mês, fonte, categoria e texto.
- **Ciclo de fatura** configurável por fonte (fechamento + vencimento).
- **Parcelamentos** no crédito com duas formas de entrada (total ou valor da parcela), primeira parcela respeitando o fechamento.
- **Gastos fixos** com recorrência flexível (mensal, anual, semanal, a cada N meses) e confirmação de valor real.
- **Orçamento** alvo total + por categoria com alertas automáticos (80% / 90% / 100%).
- **Metas** de economia com progresso acumulado.
- **Relatórios** com gráficos de evolução mensal e breakdown por categoria (Chart.js).
- **Projeção** dos próximos 3/6/12 meses considerando fixos + parcelas.
- **Responsivo** para desktop, tablet e mobile.

## Stack

- Python 3.12 + FastAPI + HTMX + Jinja2
- SQLAlchemy 2 + Alembic
- PostgreSQL 16
- Chart.js (via CDN)
- Docker + docker compose

## Pré-requisitos

- Docker e docker compose v2 instalados.
- Git.

## Primeira execução

```bash
git clone git@github.com:Robsonvieira26/MyFinanceApp.git
cd MyFinanceApp
cp .env.example .env
# edite .env e defina POSTGRES_PASSWORD (não use a senha default)
docker compose up -d --build
docker compose exec web alembic upgrade head
```

Acesse em `http://<host>:8765`.

## Portas

| Serviço    | Host | Container |
|------------|------|-----------|
| Web        | 8765 | 8000      |
| PostgreSQL | 5433 | 5432      |

Portas não-padrão propositalmente — se precisar mudar, ajuste `docker-compose.yml`.

## Operação

### Atualização segura

```bash
./scripts/update.sh
```

Fluxo:
1. Backup automático (`backup.sh`)
2. `git pull origin main`
3. `docker compose build`
4. `docker compose up -d`
5. `alembic upgrade head`

### Backup manual

```bash
./scripts/backup.sh
```

Gera `backups/finance_YYYY-MM-DD_HHMMSS.sql.gz`. Mantém os últimos 14 (override via `BACKUP_RETENTION`).

### Restauração

```bash
./scripts/restore.sh backups/finance_2026-04-23_193000.sql.gz
```

Pede confirmação digitando `yes`. Para o web, restaura o dump, sobe novamente.

### Agendamento recomendado (crontab do host)

```cron
# Backup diário às 03:30
30 3 * * * cd /caminho/para/MyFinanceApp && ./scripts/backup.sh >> /var/log/finance-backup.log 2>&1
```

## Estrutura

```
app/
  models/       SQLAlchemy
  schemas/      Pydantic
  services/     regras de negócio puras (testáveis sem HTTP)
  routers/      endpoints HTTP
  templates/    Jinja2 + HTMX
  static/       CSS + JS
migrations/     Alembic versions
tests/
  services/     testes das regras puras
  routers/      testes dos endpoints
scripts/        update.sh, backup.sh, restore.sh
docker/         Dockerfile + init.sql
docs/
  superpowers/  spec e plano de implementação
```

## Testes

```bash
docker compose run --rm web pytest -v
```

## Troubleshooting

**Web não sobe após update:**
```bash
docker compose logs web | tail -50
```

**Banco corrompido ou migration travada:**
Restaurar o último backup bom:
```bash
./scripts/restore.sh backups/<último-bom>.sql.gz
```

**Esqueci a senha do banco:**
Está em `.env`. Se perdeu, recrie o volume (perde dados — restaure do backup):
```bash
docker compose down -v   # CUIDADO: apaga volume
# editar .env com nova senha
docker compose up -d --build
./scripts/restore.sh backups/<dump>.sql.gz
```

## Contribuição

Projeto pessoal. Não aceita PRs externos.

## Licença

Uso pessoal.
````

- [ ] **Step 12.4.2: Commit e push**

```bash
git add README.md
git commit -m "docs: README final com operação, troubleshooting e agendamento de backup"
git push origin main
```

---

### Task 12.5: Tag de release v0.1.0

**Files:**
- (nenhum arquivo — só tag git)

- [ ] **Step 12.5.1: Criar tag anotada**

```bash
git tag -a v0.1.0 -m "MyFinanceApp v0.1.0 — release inicial completa

Funcionalidades:
- Dashboard com hero, métricas e grid-3
- Lançamentos (CRUD + filtros)
- Ciclo de fatura do cartão de crédito
- Parcelamentos (2 formas de entrada)
- Fixos com 4 tipos de recorrência
- Orçamento total + por categoria com alertas
- Metas de economia
- Relatórios com gráficos
- Projeção de N meses
- UI responsiva
- Scripts de backup/restore/update"
git push origin v0.1.0
```

- [ ] **Step 12.5.2: Verificar**

```bash
git tag -l
# Expected: v0.1.0
```

---

**Marco M12 alcançado — v0.1.0 PRONTA.** Sistema completo, operacional, testado, responsivo e documentado. Scripts de operação publicados. Pronto para uso no servidor caseiro.

---

## Appendix — Checklist pós-execução

Antes de considerar o projeto "entregue", confirme:

- [ ] Todos os 12 marcos concluídos com commits publicados em `main`
- [ ] Todos os testes passam: `docker compose run --rm web pytest -v`
- [ ] Build limpo: `docker compose build` sem erros
- [ ] Todas as migrations aplicadas: `alembic current` mostra o head
- [ ] Seed populou categorias e fontes: `SELECT * FROM sources; SELECT * FROM categories;`
- [ ] Teste manual em 3 viewports (1440 / 900 / 375) em cada página
- [ ] `update.sh`, `backup.sh`, `restore.sh` rodam sem erros
- [ ] README tem screenshot atualizada
- [ ] Cron diário de backup configurado no host
- [ ] `.env` protegido (permissões 600) e fora do git
- [ ] Tag v0.1.0 empurrada

---

*Fim do plano.*
