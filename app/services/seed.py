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
