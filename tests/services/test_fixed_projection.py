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
    rule = _mk_rule(seeded)
    occurrences = svc.project_rule(rule, start=date(2026, 4, 1), end=date(2026, 6, 30))
    assert occurrences == [date(2026, 4, 5), date(2026, 5, 5), date(2026, 6, 5)]


def test_monthly_skips_before_active_from(seeded):
    rule = _mk_rule(seeded, active_from=date(2026, 5, 10))
    occurrences = svc.project_rule(rule, start=date(2026, 4, 1), end=date(2026, 6, 30))
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
    rule = _mk_rule(seeded, recurrence="weekly", day_of_week=0, day_of_month=None,
                    active_from=date(2026, 4, 1))
    occ = svc.project_rule(rule, start=date(2026, 4, 1), end=date(2026, 4, 30))
    assert occ == [date(2026, 4, 6), date(2026, 4, 13),
                   date(2026, 4, 20), date(2026, 4, 27)]


def test_every_n_months_with_interval_3(seeded):
    rule = _mk_rule(seeded, recurrence="every_n_months", interval_months=3,
                    day_of_month=15, active_from=date(2026, 1, 15))
    occ = svc.project_rule(rule, start=date(2026, 1, 1), end=date(2026, 12, 31))
    assert occ == [date(2026, 1, 15), date(2026, 4, 15),
                   date(2026, 7, 15), date(2026, 10, 15)]


def test_unknown_recurrence_raises(seeded):
    rule = _mk_rule(seeded, recurrence="yearly")
    with pytest.raises(ValueError, match="recurrence"):
        svc.project_rule(rule, start=date(2026, 1, 1), end=date(2026, 12, 31))
