from src.database.sql_database.sql_alchemy.base import Base 
from sqlalchemy.orm import Mapped , mapped_column
from sqlalchemy import String , Integer , ForeignKey






class Documents(Base):
    __tablename__ = "user_documents"

    id : Mapped[int] = mapped_column(
        primary_key = True , 
        autoincrement = True
    )
    session_id : Mapped[int] = mapped_column(
        nullable = False
    )
    file_name : Mapped[str] = mapped_column(
        nullable = False
    )
    user_id : Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )