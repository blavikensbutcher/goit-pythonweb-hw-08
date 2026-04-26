
from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class ContactModel(Base):
    __tablename__ = "contacts"

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default=uuid4, unique=True, index=True
    )
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    birthday: Mapped[date] = mapped_column(Date())
    description: Mapped[str] = mapped_column(String(255), nullable=True)
