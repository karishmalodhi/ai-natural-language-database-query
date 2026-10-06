from database.mongodb_connection import collection


# ==========================================
# MONGODB QUERY SECURITY VALIDATION
# ==========================================

def validate_mongodb_query(query):

    if not isinstance(query, dict):
        return False, "Invalid MongoDB query format."

    allowed_fields = {
        "name",
        "city",
        "age",
        "email"
    }

    blocked_operators = {
        "$where",
        "$function",
        "$accumulator",
        "$expr",
        "$eval",
        "$out",
        "$merge"
    }

    for key in query.keys():

        if key in blocked_operators:
            return False, f"MongoDB operator '{key}' is not allowed."

        if key.startswith("$"):
            return False, f"MongoDB operator '{key}' is not allowed."

        if key not in allowed_fields:
            return False, f"Field '{key}' is not allowed."

    return True, "MongoDB query is safe."


# ==========================================
# EXECUTE MONGODB QUERY
# ==========================================

def execute_mongodb_query(query):

    try:

        is_safe, message = validate_mongodb_query(query)

        if not is_safe:
            raise Exception(message)

        results = list(
            collection.find(query)
        )

        # ==================================
        # REMOVE SENSITIVE PII
        # ==================================

        for document in results:

            if "_id" in document:
                document["_id"] = str(document["_id"])

            # Do not expose email to frontend/AI
            if "email" in document:
                del document["email"]

        return results

    except Exception as e:

        raise Exception(
            f"MongoDB query failed: {str(e)}"
        )