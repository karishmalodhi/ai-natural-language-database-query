from pymongo import MongoClient

MONGO_URL = "mongodb://localhost:27017"

client = MongoClient(MONGO_URL)

db = client["ai_query_db"]
collection = db["customers"]

print("MongoDB connection setup ready!")

try:
    client.admin.command("ping")
    print("MongoDB connected successfully!")
except Exception as e:
    print("Connection failed:", e)