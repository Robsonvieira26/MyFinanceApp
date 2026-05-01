from calendar import monthrange
from datetime import date


def _add_months(base: date, months: int) -> date:
    month_index = base.month - 1 + months
    year = base.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, base.day)


def fatura_due_month(
    transaction_date: date, closing_day: int, due_day: int
) -> date:
    """Returns the actual payment due date for a purchase."""
    if not (1 <= closing_day <= 28):
        raise ValueError("closing_day deve estar entre 1 e 28")
    if not (1 <= due_day <= 28):
        raise ValueError("due_day deve estar entre 1 e 28")

    if transaction_date.day <= closing_day:
        base_month = transaction_date.replace(day=1)
    else:
        base_month = _add_months(transaction_date.replace(day=1), 1)

    if due_day >= closing_day:
        due = base_month.replace(day=due_day)
    else:
        due = _add_months(base_month, 1).replace(day=due_day)

    return due


def fatura_bill_date(purchase_date: date, closing_day: int) -> date:
    """Returns the last day of the billing reference month for a purchase.

    A purchase on Apr 4 with closing_day=3 belongs to the *April* bill
    (cycle Apr 4 → May 3), so returns Apr 30. A purchase on May 1 also
    belongs to the April bill, so also returns Apr 30.
    """
    if not (1 <= closing_day <= 28):
        raise ValueError("closing_day deve estar entre 1 e 28")

    if purchase_date.day > closing_day:
        # Still within the current month's open cycle
        year, month = purchase_date.year, purchase_date.month
    else:
        # Falls in previous month's cycle (bill already closed)
        if purchase_date.month == 1:
            year, month = purchase_date.year - 1, 12
        else:
            year, month = purchase_date.year, purchase_date.month - 1

    last_day = monthrange(year, month)[1]
    return date(year, month, last_day)
