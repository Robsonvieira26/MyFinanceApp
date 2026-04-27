from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TransactionBase(BaseModel):
    description: str = Field(min_length=1, max_length=200)
    amount: Decimal = Field(gt=0, decimal_places=2)
    date: date
    source_id: int
    category_id: int
    payment_mode: Literal["credit", "debit", "pix"]
    type: Literal["expense", "income"] = "expense"
    note: str | None = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    description: str | None = Field(default=None, min_length=1, max_length=200)
    amount: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    date: date | None = None
    source_id: int | None = None
    category_id: int | None = None
    payment_mode: Literal["credit", "debit", "pix"] | None = None
    type: Literal["expense", "income"] | None = None
    note: str | None = None


class TransactionOut(TransactionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    origin: Literal["manual", "installment", "fixed"]
    status: Literal["confirmed", "projected"]
