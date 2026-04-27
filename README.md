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
