from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class FixedRuleCreate(BaseModel):
    description: str = Field(min_length=1, max_length=200)
    expected_amount: Decimal = Field(gt=0, decimal_places=2)
    recurrence: Literal["monthly", "annual", "weekly", "every_n_months"]
    source_id: int
    category_id: int
    payment_mode: Literal["credit", "debit", "pix"]
    type: Literal["expense", "income"] = "expense"
    active_from: date
    active_until: date | None = None
    interval_months: int | None = None
    day_of_month: int | None = Field(default=None, ge=1, le=31)
    day_of_week: int | None = Field(default=None, ge=0, le=6)
    anchor_month: int | None = Field(default=None, ge=1, le=12)

    @model_validator(mode="after")
    def _check_fields(self) -> "FixedRuleCreate":
        r = self.recurrence
        if r == "monthly" and self.day_of_month is None:
            raise ValueError("monthly requer day_of_month")
        if r == "annual" and (self.day_of_month is None or self.anchor_month is None):
            raise ValueError("annual requer day_of_month e anchor_month")
        if r == "weekly" and self.day_of_week is None:
            raise ValueError("weekly requer day_of_week")
        if r == "every_n_months" and (
            self.interval_months is None or self.day_of_month is None
        ):
            raise ValueError("every_n_months requer interval_months e day_of_month")
        return self
