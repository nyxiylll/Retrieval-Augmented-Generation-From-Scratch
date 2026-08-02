from src.database.sql_database.sql_alchemy.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer
from datetime import datetime
from uuid import UUID


class User(Base):
    __tablename__ = "users"

    id : Mapped[int] = mapped_column(
        primary_key = True,
        autoincrement = True,
        nullable = False
        )
    session_id : Mapped[str] = mapped_column(
        unique = True,
        nullable = False
        )
    doc_count : Mapped[int] = mapped_column(
        nullable = False,
        default = 0
        )
    query_count : Mapped[int] = mapped_column(
            nullable = False,
            default = 0
        )
    last_query_time : Mapped[datetime] = mapped_column(
        nullable = True   
        )
    account_created : Mapped[datetime] = mapped_column(
        default = datetime,
        nullable = False
        )

    