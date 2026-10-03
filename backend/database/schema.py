from sqlalchemy import inspect
from database.connection import engine


def get_sql_schema():
    inspector = inspect(engine)

    schema = {}

    for table in inspector.get_table_names():
        columns = inspector.get_columns(table)

        schema[table] = []

        for column in columns:
            schema[table].append({
                "name": column["name"],
                "type": str(column["type"])
            })

    return schema


if __name__ == "__main__":
    schema = get_sql_schema()

    print("PostgreSQL Schema:")

    for table, columns in schema.items():
        print(f"\nTable: {table}")

        for column in columns:
            print(f"- {column['name']} : {column['type']}")