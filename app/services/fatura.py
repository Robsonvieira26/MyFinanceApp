from datetime import date


def _add_months(base: date, months: int) -> date:
    month_index = base.month - 1 + months
    year = base.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, base.day)


def fatura_due_month(
    transaction_date: date, closing_day: int, due_day: int
) -> date:
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
