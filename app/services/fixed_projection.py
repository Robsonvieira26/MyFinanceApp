from calendar import monthrange
from datetime import date, timedelta

from app.models import FixedRule


def _clamp_day(year: int, month: int, day: int) -> date:
    max_day = monthrange(year, month)[1]
    return date(year, month, min(day, max_day))


def _add_months(base: date, months: int) -> date:
    month_index = base.month - 1 + months
    year = base.year + month_index // 12
    month = month_index % 12 + 1
    return _clamp_day(year, month, base.day)


def project_rule(rule: FixedRule, *, start: date, end: date) -> list[date]:
    if start > end:
        return []

    lower = max(start, rule.active_from)
    upper = end if rule.active_until is None else min(end, rule.active_until)
    if lower > upper:
        return []

    recurrence = rule.recurrence
    results: list[date] = []

    if recurrence == "monthly":
        if rule.day_of_month is None:
            raise ValueError("monthly requer day_of_month")
        cur = _clamp_day(lower.year, lower.month, rule.day_of_month)
        if cur < lower:
            cur = _add_months(cur, 1)
        while cur <= upper:
            if cur >= rule.active_from:
                results.append(cur)
            cur = _add_months(cur, 1)

    elif recurrence == "annual":
        if rule.day_of_month is None or rule.anchor_month is None:
            raise ValueError("annual requer day_of_month e anchor_month")
        for year in range(lower.year, upper.year + 1):
            cur = _clamp_day(year, rule.anchor_month, rule.day_of_month)
            if lower <= cur <= upper and cur >= rule.active_from:
                results.append(cur)

    elif recurrence == "weekly":
        if rule.day_of_week is None:
            raise ValueError("weekly requer day_of_week (0=seg..6=dom)")
        cur = lower
        offset = (rule.day_of_week - cur.weekday()) % 7
        cur = cur + timedelta(days=offset)
        while cur <= upper:
            if cur >= rule.active_from:
                results.append(cur)
            cur = cur + timedelta(days=7)

    elif recurrence == "every_n_months":
        if rule.interval_months is None or rule.day_of_month is None:
            raise ValueError("every_n_months requer interval_months e day_of_month")
        anchor = _clamp_day(
            rule.active_from.year, rule.active_from.month, rule.day_of_month
        )
        cur = anchor
        while cur < lower:
            cur = _add_months(cur, rule.interval_months)
        while cur <= upper:
            results.append(cur)
            cur = _add_months(cur, rule.interval_months)

    else:
        raise ValueError(f"recurrence inválida: {recurrence}")

    return results
