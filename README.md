# MyFinanceApp

Sistema pessoal de finanças — dashboard mensal com ciclo de fatura de cartão de crédito, gastos fixos recorrentes, parcelamentos, metas e projeções futuras. Executa em Docker no servidor caseiro.

Projeto monousuário, sem login, desenhado para uso em rede local.

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
