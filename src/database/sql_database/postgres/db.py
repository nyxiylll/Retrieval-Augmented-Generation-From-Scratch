import psycopg
import logging



logger = logging.getLogger(__name__)

from contextlib import asynccontextmanager 


class PostgresDataBase:

    def __init__(self,
                    host : str,
                    dbname : str,
                    user : str,
                    sslmode : str , 
                    password : str ,
                    connect_timeout : int = 10,
                    port : int = 5432,
                    ):

        self.host = host
        self.dbname = dbname
        self.user = user
        self.sslmode = sslmode
        self.password = password
        self.connect_timeout = connect_timeout
        self.port = port


    @asynccontextmanager
    async def _create_async_connection(self):
        try:
            connection = await psycopg.AsyncConnection.connect(
                f"host={self.host} port={self.port} dbname={self.dbname} user={self.user} sslmode={self.sslmode} connect_timeout={self.connect_timeout} password={self.password}"
            )
            async with connection.cursor() as cursor:

                yield connection

        except:
            raise ConnectionError(
                f"Failed to connect to Database"
            )
