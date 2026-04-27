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
