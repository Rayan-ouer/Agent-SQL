import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine

def patched_correct_for_mysql_bugs(*args, **kwargs):
    pass

def create_engine_for_sql_database(connection_string: str):
    username = quote_plus(os.getenv("AI_USERNAME"))
    password = quote_plus(os.getenv("AI_PASSWORD"))
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    database = os.getenv("DB_DATABASE")
    url = f"{connection_string}//{username}:{password}@{host}:{port}/{database}"
    print("URL: ", url)
    engine = create_engine(
        url,
        pool_pre_ping=True,
        pool_recycle=28800,
        echo=False,
    )
    return engine