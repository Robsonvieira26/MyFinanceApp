"""Insere dados de demonstração. Roda dentro do container: python scripts/seed_demo.py"""
import sys, os
sys.path.insert(0, "/app")

from datetime import date
from decimal import Decimal

from app.db import SessionLocal
from app.services.seed import seed_all
from app.services import transactions as tx_svc, budgets as bud_svc, goals as goal_svc
from app.services import fixed as fixed_svc, installments as inst_svc
from app.models import Source, Category

db = SessionLocal()

# ── Seed bases ──────────────────────────────────────────────────────────────
seed_all(db)

# Resolve IDs by slug
def src(slug):  return db.query(Source).filter_by(slug=slug).first().id
def cat(slug):  return db.query(Category).filter_by(slug=slug).first().id

SRC_CONTA   = src("conta-principal")
SRC_VA      = src("va")
SRC_VT      = src("vt")
CAT_MORADIA = cat("moradia")
CAT_MERCADO = cat("mercado")
CAT_TRANSP  = cat("transporte")
CAT_ALIM    = cat("alimentacao")
CAT_LAZER   = cat("lazer")
CAT_SAUDE   = cat("saude")
CAT_ASSIN   = cat("assinaturas")
CAT_EDU     = cat("educacao")
CAT_OUT     = cat("outros")

Y, M = 2026, 4

def tx(desc, amount, day, source_id, category_id, mode="credit", kind="expense"):
    tx_svc.create(db, {
        "description": desc,
        "amount": Decimal(str(amount)),
        "date": date(Y, M, day),
        "source_id": source_id,
        "category_id": category_id,
        "payment_mode": mode,
        "type": kind,
        "status": "confirmed",
    })

# ── Receita ──────────────────────────────────────────────────────────────────
tx("Salário abril",          5500.00,  5, SRC_CONTA, CAT_OUT,    mode="pix",   kind="income")

# ── Moradia ──────────────────────────────────────────────────────────────────
tx("Aluguel",                1800.00,  5, SRC_CONTA, CAT_MORADIA, mode="debit")
tx("Condomínio",               320.00,  8, SRC_CONTA, CAT_MORADIA, mode="debit")
tx("Energia elétrica",         180.00, 10, SRC_CONTA, CAT_MORADIA, mode="debit")

# ── Mercado ──────────────────────────────────────────────────────────────────
tx("Mercado semanal",          280.00,  6, SRC_CONTA, CAT_MERCADO, mode="credit")
tx("Mercado semanal",          310.00, 13, SRC_CONTA, CAT_MERCADO, mode="credit")
tx("Hortifruti",                95.00, 20, SRC_VA,    CAT_MERCADO, mode="debit")
tx("Mercado semanal",          295.00, 22, SRC_CONTA, CAT_MERCADO, mode="credit")

# ── Transporte ───────────────────────────────────────────────────────────────
tx("Passagem semanal",         220.00,  4, SRC_VT,    CAT_TRANSP,  mode="debit")
tx("Uber corrida",              42.00, 11, SRC_CONTA, CAT_TRANSP,  mode="credit")
tx("Uber corrida",              38.00, 18, SRC_CONTA, CAT_TRANSP,  mode="credit")
tx("Estacionamento",            30.00, 24, SRC_CONTA, CAT_TRANSP,  mode="credit")

# ── Alimentação ──────────────────────────────────────────────────────────────
tx("Almoço restaurante",        48.00,  9, SRC_CONTA, CAT_ALIM,   mode="credit")
tx("iFood jantar",              62.00, 15, SRC_CONTA, CAT_ALIM,   mode="credit")
tx("Café padaria",              18.00, 17, SRC_CONTA, CAT_ALIM,   mode="debit")
tx("Almoço exec",               35.00, 23, SRC_CONTA, CAT_ALIM,   mode="credit")

# ── Lazer ─────────────────────────────────────────────────────────────────────
tx("Cinema",                    52.00, 12, SRC_CONTA, CAT_LAZER,  mode="credit")
tx("Barzinho c/ amigos",       130.00, 19, SRC_CONTA, CAT_LAZER,  mode="credit")
tx("Jogo Steam",                35.00, 21, SRC_CONTA, CAT_LAZER,  mode="credit")

# ── Saúde ─────────────────────────────────────────────────────────────────────
tx("Farmácia",                  68.00,  7, SRC_CONTA, CAT_SAUDE,  mode="credit")
tx("Academia mensalidade",     120.00,  3, SRC_CONTA, CAT_SAUDE,  mode="debit")

# ── Assinaturas ───────────────────────────────────────────────────────────────
tx("Netflix",                   55.90, 10, SRC_CONTA, CAT_ASSIN,  mode="credit")
tx("Spotify",                   21.90, 10, SRC_CONTA, CAT_ASSIN,  mode="credit")
tx("GitHub Copilot",            43.00, 10, SRC_CONTA, CAT_ASSIN,  mode="credit")

# ── Educação ──────────────────────────────────────────────────────────────────
tx("Udemy curso",               29.90, 14, SRC_CONTA, CAT_EDU,    mode="credit")

# ── Outros ────────────────────────────────────────────────────────────────────
tx("Presente aniversário",      89.00, 16, SRC_CONTA, CAT_OUT,    mode="credit")

# ── Orçamento ────────────────────────────────────────────────────────────────
bud_svc.set_total(db, Decimal("4000.00"))
bud_svc.set_category(db, category_id=CAT_MERCADO,  amount=Decimal("1200.00"))
bud_svc.set_category(db, category_id=CAT_TRANSP,   amount=Decimal("400.00"))
bud_svc.set_category(db, category_id=CAT_LAZER,    amount=Decimal("300.00"))
bud_svc.set_category(db, category_id=CAT_ASSIN,    amount=Decimal("150.00"))

# ── Metas ─────────────────────────────────────────────────────────────────────
goal_svc.create(db, {
    "title": "Reserva de emergência",
    "target_amount": Decimal("18000.00"),
    "saved_amount": Decimal("4200.00"),
    "target_date": date(2027, 1, 1),
    "note": "6 meses de despesas",
})
goal_svc.create(db, {
    "title": "Viagem Europa",
    "target_amount": Decimal("12000.00"),
    "saved_amount": Decimal("1800.00"),
    "target_date": date(2027, 6, 1),
    "note": "Julho 2027 — Portugal + Espanha",
})
goal_svc.create(db, {
    "title": "Notebook novo",
    "target_amount": Decimal("6500.00"),
    "saved_amount": Decimal("3000.00"),
    "target_date": date(2026, 9, 1),
})

# ── Gastos fixos ─────────────────────────────────────────────────────────────
fixed_svc.create_rule(db, {
    "description": "Aluguel",
    "expected_amount": Decimal("1800.00"),
    "source_id": SRC_CONTA,
    "category_id": CAT_MORADIA,
    "payment_mode": "debit",
    "recurrence": "monthly",
    "day_of_month": 5,
    "active_from": date(2026, 1, 1),
})
fixed_svc.create_rule(db, {
    "description": "Academia",
    "expected_amount": Decimal("120.00"),
    "source_id": SRC_CONTA,
    "category_id": CAT_SAUDE,
    "payment_mode": "debit",
    "recurrence": "monthly",
    "day_of_month": 3,
    "active_from": date(2026, 1, 1),
})
fixed_svc.create_rule(db, {
    "description": "Netflix",
    "expected_amount": Decimal("55.90"),
    "source_id": SRC_CONTA,
    "category_id": CAT_ASSIN,
    "payment_mode": "credit",
    "recurrence": "monthly",
    "day_of_month": 10,
    "active_from": date(2026, 1, 1),
})

# ── Parcelamento ─────────────────────────────────────────────────────────────
inst_svc.create_plan(db, {
    "description": "iPhone 15 Pro",
    "total_amount": Decimal("7200.00"),
    "installments_count": 12,
    "input_mode": "total",
    "source_id": SRC_CONTA,
    "category_id": CAT_OUT,
    "first_purchase_date": date(2026, 3, 1),
})

db.close()
print("✓ Dados de demo inseridos com sucesso.")
