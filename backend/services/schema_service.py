from database.schema import get_sql_schema
from database.mongodb_connection import collection


def get_mongo_schema():
    documents = collection.find().limit(5)

    fields = set()

    for document in documents:
        fields.update(document.keys())

    return {
        "customers": sorted(fields)
    }


def get_all_schema():
    return {
        "postgresql": get_sql_schema(),
        "mongodb": get_mongo_schema()
    }


if __name__ == "__main__":
    schema = get_all_schema()

    print("===== DATABASE SCHEMA =====")
    print(schema)
    