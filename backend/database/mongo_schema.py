from database.mongodb_connection import collection

documents = collection.find().limit(5)

fields = set()

for document in documents:
    fields.update(document.keys())

print("MongoDB Collection: customers")
print("\nFields:")

for field in sorted(fields):
    print("-", field)