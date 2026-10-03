from sqlalchemy import text
from database.connection import engine


def execute_sql(sql):
    with engine.connect() as connection:
        result = connection.execute(text(sql))

        rows = result.mappings().all()

        return [dict(row) for row in rows]