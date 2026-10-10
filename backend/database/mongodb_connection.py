from pymongo import MongoClient


MONGO_URL = (
    "mongodb://ai_readonly:AI_ReadOnly_2026"
    "@localhost:27017/ai_query_db"
)

client = MongoClient(MONGO_URL)

db = client["ai_query_db"]
collection = db["customers"]


print("Read-only MongoDB connection setup ready!")


try:
    client.admin.command("ping")

    print(
        "MongoDB read-only connection successful!"
    )

except Exception as e:

    print(
        "MongoDB connection failed:",
        e
    )