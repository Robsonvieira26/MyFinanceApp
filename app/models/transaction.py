from datetime import date
from decimal import Decimal

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Transaction(Base, TimestampMixin):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)

    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    payment_mode: Mapped[str] = mapped_column(String(16), nullable=False)  # credit|debit|pix
    type: Mapped[str] = mapped_column(String(16), nullable=False, default="expense")  # expense|income
    origin: Mapped[str] = mapped_column(String(16), nullable=False, default="manual")  # manual|installment|fixed
    origin_ref_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    status: Mapped[str] = mapped_column(String(16), nullable=False, default="confirmed")  # confirmed|projected
    actual_amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    actual_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    note: Mapped[str | None] = mapped_column(Text, nullable=True)

    source = relationship("Source")
    category = relationship("Category")

    def compute_due_date(self, source: "Source") -> "date":
        from app.services.fatura import fatura_due_month

        if self.payment_mode in ("debit", "pix"):
            return self.date
        if source.closing_day is None or source.due_day is None:
            return self.date
        return fatura_due_month(self.date, source.closing_day, source.due_day)
