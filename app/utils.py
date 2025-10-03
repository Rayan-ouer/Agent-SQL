import os
from sqlalchemy import create_engine

def patched_correct_for_mysql_bugs(*args, **kwargs):
    pass

def create_engine_for_sql_database(connection_string: str):
    engine = create_engine(
            connection_string
            + os.getenv(("AI_USERNAME"))
            + ":"
            + os.getenv(("AI_PASSWORD"))
            + "@"
            + os.getenv(("DB_HOST"))
            + ":"
            + os.getenv(("DB_PORT"))
            + "/"
            + os.getenv(("DB_DATABASE"))
        )
    return engine