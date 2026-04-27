from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Budget(Base, TimestampMixin):
    """Orçamento alvo.

    Quando category_id é NULL → alvo total mensal.
    Quando category_id tem valor → alvo daquela categoria.
    Sempre vale "para todos os meses" (sem override por mês, conforme spec).
    """
    __tablename__ = "budgets"
    __table_args__ = (UniqueConstraint("category_id", name="uq_budget_category"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    scope: Mapped[str] = mapped_column(String(16), nullable=False)  # total|category
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"), nullable=True
    )

    category = relationship("Category")
