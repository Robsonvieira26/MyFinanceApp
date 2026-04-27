from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class InstallmentPlanCreate(BaseModel):
    description: str = Field(min_length=1, max_length=200)
    installments_count: int = Field(ge=2, le=120)
    first_purchase_date: date
    source_id: int
    category_id: int

    input_mode: Literal["total", "per_installment"]
    total_amount: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    installment_amount: Decimal | None = Field(default=None, gt=0, decimal_places=2)

    @model_validator(mode="after")
    def _check_amounts(self) -> "InstallmentPlanCreate":
        if self.input_mode == "total":
            if self.total_amount is None:
                raise ValueError("total_amount obrigatório quando input_mode='total'")
        elif self.input_mode == "per_installment":
            if self.installment_amount is None:
                raise ValueError(
                    "installment_amount obrigatório quando input_mode='per_installment'"
                )
        return self
