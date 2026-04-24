# Sistema de Finanças Pessoais — Design

**Data:** 2026-04-23
**Status:** Rascunho para revisão
**Autor:** Robson (via brainstorming com Claude)

---

## 1. Objetivo

Aplicação web pessoal para gestão financeira, executada em servidor caseiro via Docker. Foco em clareza sobre o mês corrente e o seguinte, com tratamento correto do ciclo de fatura do cartão de crédito, gastos fixos recorrentes e parcelados no crédito.

**Uso:** monousuário (sem login), acessado pelo próprio Robson em rede local.

---

## 2. Escopo

### Dentro do escopo
- Dashboard do mês corrente com orçamento, receita, saldo previsto e resumos.
- Cadastro de lançamentos: avulsos, parcelados e fixos recorrentes.
- Gestão de fontes (conta, cartões de débito VA/VT), com lógica de fatura para crédito.
- Orçamento alvo total + por categoria.
- Receitas: salário fixo + extras eventuais.
- Lista de lançamentos com filtros (data, categoria, fonte).
- Edição e exclusão de qualquer lançamento.
- Relatório histórico (gastos por categoria nos últimos N meses, gráficos).
- Projeção futura (próximos 3/6/12 meses considerando fixos + parcelas).
- Metas de economia (ex.: "juntar R$ 10k até dezembro").
- Alertas (ex.: "estourou 80% do orçamento de lazer").

### Fora do escopo (YAGNI)
- Autenticação / multi-usuário.
- Import CSV/OFX de extrato bancário.
- Export CSV.
- Integração bancária (Open Finance).
- Mobile app nativo (UI deve ser responsiva, mas é web).

---

## 3. Modelo de domínio

### 3.1 Fontes (`sources`)
Três fontes fixas, pré-cadastradas na instalação:

| Nome            | Tipo    | Comportamento                                                    |
|-----------------|---------|------------------------------------------------------------------|
| Conta Principal | `hybrid` | Aceita modos `credit`, `debit`, `pix`. Tem ciclo de fatura.     |
| VA (Alelo)      | `debit`  | Só débito. Sem ciclo de fatura.                                 |
| VT (Flash)      | `debit`  | Só débito. Sem ciclo de fatura.                                 |

**Ciclo de fatura da Conta Principal** (configurável):
- **Dia de fechamento:** 4 (padrão).
- **Dia de vencimento:** 10 do mês seguinte (padrão).
- Um lançamento no modo `credit` feito entre **05/mês M** e **04/mês M+1** cai na fatura que vence **10/mês M+1**.

### 3.2 Categorias (`categories`)
Pré-cadastradas: Moradia, Mercado, Transporte, Alimentação, Lazer, Saúde, Assinaturas, Educação, Outros.
Usuário pode criar novas, editar ou arquivar.

### 3.3 Lançamentos (`transactions`)
Um lançamento representa um movimento financeiro. Campos principais:

- `id`, `description`, `amount`, `date` (data do fato gerador / compra)
- `source_id`, `payment_mode` (`credit`/`debit`/`pix`), `category_id`
- `type`: `expense` | `income`
- `origin`: `manual` | `installment` | `fixed` (origem do lançamento)
- `origin_ref_id`: FK opcional para `installment_plans` ou `fixed_rules`
- `status`: `confirmed` | `projected` (projetados aparecem na Projeção mas não afetam saldo real até confirmados)
- `actual_amount`, `actual_date` (usados para gastos fixos com valor esperado quando o usuário confirma o real)

**Campo derivado (não armazenado — computado):**
- `due_month`: mês em que efetivamente impacta o caixa.
  - `debit`/`pix`: mês da `date` do lançamento.
  - `credit`: mês em que vence a fatura que inclui este lançamento (calculado do fechamento).

### 3.4 Parcelamentos (`installment_plans`)
Plano de parcelamento no crédito. Um plano gera N lançamentos (`origin=installment`).

Formas de cadastro:
1. **Total + número de parcelas** → sistema calcula `valor_parcela = total / n`.
2. **Valor da parcela + número** → sistema calcula `total = valor × n`.

Campos: `id`, `description`, `total_amount`, `installments_count`, `installment_amount`, `first_purchase_date` (data da compra), `source_id` (sempre crédito), `category_id`.

**Geração das parcelas:**
- Parcela 1 respeita o ciclo de fatura (compra 05/abr → parcela 1 na fatura de 10/mai).
- Parcelas 2..N caem nas faturas subsequentes (10/jun, 10/jul, ...).

### 3.5 Regras fixas (`fixed_rules`)
Regra de recorrência que projeta lançamentos futuros:

- `recurrence`: `monthly` | `annual` | `weekly` | `every_n_months` (com `interval_months`)
- `expected_amount`: valor esperado
- `day_of_month` / `day_of_week` / `month_day_combo`
- `source_id`, `payment_mode`, `category_id`
- `active_from`, `active_until` (opcional)

**Geração:** o sistema projeta lançamentos futuros com `status=projected`. Quando o mês correspondente chega (ou o usuário confirma antes), o lançamento pode ter o `actual_amount` ajustado e o `status` vira `confirmed`.

### 3.6 Orçamento (`budgets`)
- **Alvo total mensal** — um valor único, vale para todos os meses até ser alterado.
- **Alvo por categoria** — um valor por categoria, vale para todos os meses até ser alterado.
Simplificação intencional: sem override por mês específico (YAGNI — adicionar no futuro se precisar).

### 3.7 Receitas (`incomes`)
- Salário fixo: modelado como `fixed_rules` com `type=income`.
- Extras: lançamentos com `type=income`, `origin=manual`.

### 3.8 Metas (`goals`)
- `id`, `title`, `target_amount`, `target_date`, `saved_amount`, `active`
- Atualização manual do `saved_amount`.

### 3.9 Alertas (`alerts`)
Regras avaliadas no carregamento do dashboard:
- Categoria atingiu X% do alvo (padrão 80%).
- Total do mês atingiu X% do alvo (padrão 90%).
- Fatura fecha em N dias.
- Gasto fixo previsto não foi confirmado após a data esperada.

---

## 4. Regras de negócio críticas

### 4.1 Cálculo da fatura
Função pura `fatura_due_month(transaction_date, closing_day, due_day) -> Date`:
```
if transaction_date.day <= closing_day:
    fatura fecha no próprio mês → vence no mês seguinte
else:
    fatura fecha no mês seguinte → vence 2 meses depois
```

### 4.2 "Saldo previsto" no dashboard
```
saldo_previsto_fim_do_mes = receita_confirmada_do_mes
                          - gastos_débito_do_mes
                          - fatura_que_vence_no_mes
                          - fixos_débito_projetados_restantes_do_mes
                          - parcelas_de_crédito_que_compõem_a_fatura_do_mes
```

### 4.3 Geração de parcelas
Ao cadastrar um `installment_plan`, o sistema cria imediatamente os N lançamentos (`status=projected`) com as datas calculadas pelo ciclo da fatura. Isso facilita consultas de "projeção dos próximos 6 meses" sem precisar recalcular.

Edição retroativa: alterar o plano regenera as parcelas futuras não confirmadas. Parcelas já confirmadas ficam imutáveis (o usuário pode editá-las individualmente).

### 4.4 Arquivamento vs exclusão
- Categorias e fixos são **arquivados** (soft delete), nunca apagados, para preservar histórico.
- Lançamentos podem ser excluídos de fato (hard delete).

---

## 5. UI/UX

### 5.1 Direção visual
**Bloomberg Mk II com paleta roxa.** JetBrains Mono em tudo. Charcoal `#0B0E11` de fundo, texto creme `#D8D4C8`, **primária roxo `#C084FC`** (substituindo o âmbar padrão Bloomberg), verde `#4AC776` para "ok", coral `#FF8B6B` para alertas. Scanlines CRT sutis, vinheta radial, cursor `▊` piscando, box-drawing ASCII nas tabelas. Estética de terminal financeiro, data-dense.

### 5.2 Estrutura
Layout com **sidebar fixa (232px)** + **topbar** + **main**. Sidebar mostra:
- Brand `FIN//26` com glow roxo
- Session info (DB, PID, uptime, status)
- Navegação das páginas
- Footer com exercício/moeda/sync

### 5.3 Páginas

1. **Dashboard (`/`)** — Página principal.
   - Header com título + ações (adicionar, filtrar, seletor de mês).
   - Hero: número grande do gasto acumulado do mês + progress bar + 4 metrics (Receita, Saldo previsto, Queima/dia, Alertas ativos).
   - Grid de 3 painéis: **Categorias** (top 5 com %), **Fontes** (distribuição), **Sinais** (alertas resumidos).
   - Command line decorativa no rodapé.
   - **Não inclui** o ledger de maio previsto (movido para Projeção) nem ticker de alertas.

2. **Lançamentos (`/lancamentos`)** — Lista com filtros (mês, categoria, fonte, texto), edição e exclusão inline.

3. **Parcelados (`/parcelados`)** — Lista de planos ativos, com cadastro (modal com as duas formas de entrada) e visão das parcelas já pagas vs restantes.

4. **Fixos (`/fixos`)** — Lista de regras fixas ativas/arquivadas, cadastro com recorrência flexível, confirmação de valor real no mês.

5. **Relatórios (`/relatorios`)** — Histórico dos últimos N meses: gastos por categoria (barras empilhadas), evolução total, comparativo mês-a-mês.

6. **Projeção (`/projecao`)** — Visão dos próximos 3/6/12 meses. Aqui mora o ledger detalhado do próximo mês (que estava no dashboard original), mais sparkline de 6 meses com breakdown por tipo (fatura, fixos, parcelas).

7. **Metas (`/metas`)** — Cards de metas com progresso e prazo.

8. **Categorias (`/config/categorias`)** — CRUD de categorias + orçamento por categoria.

9. **Fontes (`/config/fontes`)** — Configuração de fontes (dia de fechamento, vencimento, nome do banco/cartão).

10. **Sistema (`/config/sistema`)** — Orçamento total, regras de alerta (threshold %), exercício fiscal, etc.

### 5.4 Responsividade
**Requisito:** UI responsiva para uso em desktop, tablet e mobile.
- **≥ 1200px:** layout completo com sidebar fixa + grid-3 em 3 colunas.
- **≥ 768px e < 1200px:** sidebar colapsável em drawer, grid-3 em 2 colunas ou empilhado.
- **< 768px:** sidebar vira menu hamburger, grid-3 empilhado, hero metrics em 2×2, fontes reduzidas proporcionalmente. Padding/gaps reduzidos.
- Tabelas com muitas colunas (lançamentos, parcelas) viram cards empilhados em mobile.

---

## 6. Stack técnica

| Camada       | Tecnologia                                        |
|--------------|---------------------------------------------------|
| Backend      | Python 3.12 + FastAPI                             |
| Templates    | Jinja2 (SSR) + HTMX para interatividade parcial   |
| Validação    | Pydantic v2                                       |
| ORM          | SQLAlchemy 2.x + Alembic (migrations)             |
| Banco        | PostgreSQL 16                                     |
| Gráficos     | Chart.js (client-side, importado via CDN)         |
| CSS          | CSS puro, custom properties, sem framework        |
| Fonte        | JetBrains Mono (Google Fonts)                     |
| Runtime      | Uvicorn                                           |
| Container    | Docker + docker compose                           |

**Por quê FastAPI + HTMX:** simplicidade, SSR sem complexidade de SPA, boa tipagem, baixa pegada de memória para servidor caseiro.

---

## 7. Arquitetura

### 7.1 Estrutura de diretórios
```
finance/
├── app/
│   ├── main.py                  # FastAPI app
│   ├── config.py                # Settings via env
│   ├── db.py                    # Engine, session
│   ├── models/                  # SQLAlchemy models
│   │   ├── source.py
│   │   ├── category.py
│   │   ├── transaction.py
│   │   ├── installment_plan.py
│   │   ├── fixed_rule.py
│   │   ├── budget.py
│   │   ├── goal.py
│   │   └── alert.py
│   ├── schemas/                 # Pydantic schemas
│   ├── services/                # Regras de negócio puras
│   │   ├── fatura.py            # Cálculo de ciclo de fatura
│   │   ├── installments.py      # Geração de parcelas
│   │   ├── fixed_projection.py  # Projeção de fixos
│   │   ├── dashboard.py         # Agregados do dashboard
│   │   ├── projection.py        # Projeção N meses
│   │   ├── alerts.py            # Avaliação de alertas
│   │   └── reports.py           # Relatórios históricos
│   ├── routers/                 # Endpoints FastAPI (um por página)
│   │   ├── dashboard.py
│   │   ├── transactions.py
│   │   ├── installments.py
│   │   ├── fixed.py
│   │   ├── reports.py
│   │   ├── projection.py
│   │   ├── goals.py
│   │   └── config.py
│   ├── templates/               # Jinja2
│   │   ├── base.html            # Layout (sidebar, topbar)
│   │   ├── dashboard.html
│   │   ├── _partials/           # Fragmentos para HTMX
│   │   └── ...
│   └── static/
│       ├── css/
│       │   └── app.css          # Tema Bloomberg-roxo + responsivo
│       ├── js/
│       │   └── app.js           # Chart.js init, interações mínimas
│       └── fonts/               # JetBrains Mono local (backup do CDN)
├── migrations/                  # Alembic
│   └── versions/
├── tests/
│   ├── services/                # Testes das regras puras
│   └── routers/                 # Testes dos endpoints
├── docker/
│   ├── Dockerfile               # Web
│   └── postgres/
│       └── init.sql             # Cria DB/roles
├── scripts/
│   ├── update.sh
│   ├── backup.sh
│   └── restore.sh
├── docker-compose.yml
├── pyproject.toml
├── .env.example
└── README.md
```

### 7.2 Separação services / routers
Services são **funções puras** sobre dados (recebem sessão + parâmetros, retornam DTOs). Testáveis sem HTTP. Routers cuidam de rotas, renderização e HTMX — zero lógica de negócio.

### 7.3 Projeção e parcelas armazenadas
Parcelas são materializadas no banco no momento do cadastro (economiza recálculo em toda consulta). Fixos são projetados **on-demand** para os próximos N meses (mais leves e mais flexíveis a mudanças de regra).

---

## 8. Infraestrutura (Docker)

### 8.1 `docker-compose.yml`
Dois serviços: `web` e `db`.

**Portas** (não-padrão):
- Web (host → container): **8765 → 8000**
- PostgreSQL (host → container): **5433 → 5432**

### 8.2 Persistência
Volume Docker nomeado `finance_pgdata` ligado a `/var/lib/postgresql/data`. Sobrevive a `docker compose down` e recreação.

### 8.3 Variáveis de ambiente (`.env`)
```
POSTGRES_DB=finance
POSTGRES_USER=finance
POSTGRES_PASSWORD=<gerada-na-instalação>
DATABASE_URL=postgresql+psycopg://finance:***@db:5432/finance
TZ=America/Sao_Paulo
```

### 8.4 Scripts bash (em `scripts/`)

**`update.sh`** — atualização segura com backup automático:
1. Executa `backup.sh` (dump SQL pré-update).
2. `git pull` no repositório.
3. `docker compose build`.
4. `docker compose up -d`.
5. Roda `alembic upgrade head` dentro do container web.
6. Mostra status final.
Em caso de falha em qualquer etapa, avisa o usuário mas **não** restaura automaticamente (requer intervenção manual via `restore.sh`).

**`backup.sh`** — dump manual:
- Executa `pg_dump` dentro do container `db`.
- Salva em `./backups/finance_YYYY-MM-DD_HHMMSS.sql.gz`.
- Mantém últimos N backups (rotação configurável, padrão 14).

**`restore.sh <arquivo.sql.gz>`** — restauração:
- Valida que o arquivo existe.
- Pede confirmação explícita (`yes` digitado).
- Para o container web.
- Drop + create do schema.
- Aplica o dump.
- Reinicia web.

Todos os scripts são idempotentes e começam com `set -euo pipefail`.

---

## 9. Não-funcionais

- **Performance:** consulta do dashboard deve retornar em < 200ms em base com 10 anos de histórico (~50k lançamentos).
- **Memória:** containers não devem exceder 512MB em uso normal (web: ~200MB, db: ~200MB).
- **Tempo de inicialização:** `docker compose up` pronto para servir em < 15s.
- **Segurança:** banco só escuta em rede Docker interna. Apenas a porta 8765 fica exposta ao host. Senhas armazenadas em `.env` (fora do git).
- **Logs:** stdout estruturado (JSON em produção, texto legível em dev). Retenção pelo próprio Docker.

---

## 10. Git, GitHub e documentação

### 10.1 Repositório
- **Remote:** `git@github.com:Robsonvieira26/MyFinanceApp.git`
- **Branch única:** `main` (projeto monousuário, sem PRs).
- **Inicialização:** feita na primeira etapa do plano — `git init` no diretório, `git remote add origin <url>`, primeiro commit com estrutura base + README.

### 10.2 Cadência de commits
**Um commit por passo do plano de implementação.** Cada tarefa concluída (não apenas cada milestone) vira um commit com mensagem descritiva e é imediatamente empurrado para o remote com `git push origin main`.

Formato da mensagem:
```
<tipo>: <descrição curta>

<corpo opcional com racional / contexto>
```
Tipos: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `style`, `infra`.

Exemplos:
- `infra: inicializa projeto com docker compose e postgres`
- `feat: CRUD de lançamentos avulsos`
- `feat: cálculo de ciclo de fatura (fechamento dia 4, venc. 10)`
- `feat: dashboard com hero, grid-3 e paleta Bloomberg-roxa`
- `docs: atualiza README com instruções de deploy`

### 10.3 README.md
Na raiz do repositório, em português, contendo:
- **Visão geral** — o que o app faz em 2 parágrafos.
- **Screenshot** do dashboard (adicionado quando estiver pronto).
- **Stack** — lista resumida (FastAPI + HTMX + Postgres + Docker).
- **Pré-requisitos** — Docker + docker compose, Git.
- **Instalação/primeira execução:**
  ```bash
  git clone git@github.com:Robsonvieira26/MyFinanceApp.git
  cd MyFinanceApp
  cp .env.example .env   # edite a senha do postgres
  docker compose up -d
  ```
- **Acesso** — `http://<host>:8765`.
- **Atualização** — `./scripts/update.sh` (faz backup → git pull → rebuild).
- **Backup manual** — `./scripts/backup.sh`.
- **Restauração** — `./scripts/restore.sh backups/<arquivo>.sql.gz`.
- **Portas usadas** — 8765 (web) e 5433 (postgres no host).
- **Estrutura do projeto** — árvore resumida dos diretórios principais.
- **Contribuição** — nota curta: "projeto pessoal, não aceita PRs externos".

O README é **vivo** — deve ser atualizado no mesmo commit em que features relevantes ao deploy são introduzidas.

---

## 11. Open questions (para o plano de implementação)

- Seed inicial de categorias/fontes: rodar como migration Alembic ou script Python à parte?
- Estratégia de teste do cálculo de fatura: snapshot tests com datas fixas cobrindo os casos de virada de mês/ano.
- Locale para formatação (R$, datas DD/MM/YYYY): usar Babel ou format manual? (Provavelmente manual, é só `pt_BR`.)
- Onde rodam os cron jobs internos (ex.: rotação de backups)? Supervisord dentro do container web ou cron do host? (Recomendação: cron do host acionando `backup.sh`; mantém o container stateless.)

---

## 11. Milestones (prévios — serão refinados no plano)

1. **M1 — Fundação:** `git init`, remote configurado, README.md inicial, `.gitignore`, `.env.example`, estrutura base FastAPI + Docker + Postgres + Alembic + seed de categorias/fontes, página "Hello" estilizada. Primeiro push para `main`.
2. **M2 — Lançamentos básicos:** CRUD de transações avulsas + lista com filtros.
3. **M3 — Fatura de crédito:** cálculo de `due_month` + apresentação distinta débito vs crédito.
4. **M4 — Dashboard v1:** hero + grid-3 com dados reais.
5. **M5 — Parcelamentos:** plano + geração de parcelas + UI de cadastro nas duas formas.
6. **M6 — Fixos:** regras recorrentes + projeção + confirmação de valor real.
7. **M7 — Orçamento + Alertas:** alvo total e por categoria + avaliação de alertas no dashboard.
8. **M8 — Metas:** CRUD + visão no dashboard.
9. **M9 — Relatórios históricos:** gráficos de evolução.
10. **M10 — Projeção:** página dedicada com ledger do próximo mês + sparkline N meses.
11. **M11 — Responsividade:** ajustes para mobile/tablet.
12. **M12 — Scripts de operação:** update/backup/restore, `.env.example`, README de deploy.
