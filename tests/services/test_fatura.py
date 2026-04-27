from datetime import date

import pytest

from app.services.fatura import fatura_due_month


def test_purchase_before_closing_lands_in_current_month_invoice():
    assert fatura_due_month(date(2026, 4, 3), closing_day=4, due_day=10) == date(2026, 4, 10)


def test_purchase_on_closing_day_still_current_cycle():
    assert fatura_due_month(date(2026, 4, 4), closing_day=4, due_day=10) == date(2026, 4, 10)


def test_purchase_day_after_closing_rolls_to_next_cycle():
    assert fatura_due_month(date(2026, 4, 5), closing_day=4, due_day=10) == date(2026, 5, 10)


def test_purchase_late_in_month_rolls_to_next_cycle():
    assert fatura_due_month(date(2026, 4, 30), closing_day=4, due_day=10) == date(2026, 5, 10)


def test_december_purchase_after_closing_rolls_to_january():
    assert fatura_due_month(date(2026, 12, 15), closing_day=4, due_day=10) == date(2027, 1, 10)


def test_december_purchase_before_closing_stays_in_december():
    assert fatura_due_month(date(2026, 12, 2), closing_day=4, due_day=10) == date(2026, 12, 10)


def test_custom_closing_and_due():
    assert fatura_due_month(date(2026, 4, 19), closing_day=20, due_day=5) == date(2026, 5, 5)
    assert fatura_due_month(date(2026, 4, 21), closing_day=20, due_day=5) == date(2026, 6, 5)


def test_february_edge_28_days():
    assert fatura_due_month(date(2026, 2, 28), closing_day=4, due_day=10) == date(2026, 3, 10)


def test_invalid_closing_day_raises():
    with pytest.raises(ValueError):
        fatura_due_month(date(2026, 4, 1), closing_day=32, due_day=10)


def test_invalid_due_day_raises():
    with pytest.raises(ValueError):
        fatura_due_month(date(2026, 4, 1), closing_day=4, due_day=0)
