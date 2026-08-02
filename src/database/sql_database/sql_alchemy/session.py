from sqlalchemy import create_engine
from src.database.sql_database.sql_alchemy.base import Base
import asyncio
from src.database.sql_database.sql_alchemy.models.document import Documents
from src.database.sql_database.sql_alchemy.models.user import User

engine = create_engine(
    url = "",
    echo = False
    )


print("Done")

if __name__ == "__main__":
    Base.metadata.create_all(engine)
