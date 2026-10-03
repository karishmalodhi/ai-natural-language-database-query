from services.llm_service import generate_sql
from database.utils.sql_validator import validate_sql
from services.db_service import execute_sql


schema = """
customers(
    id INTEGER,
    name VARCHAR(100),
    city VARCHAR(100),
    age INTEGER,
    email VARCHAR(150)
)
"""

question = "Show me all customers from Agra"


# 1. Generate SQL
sql = generate_sql(question, schema)

print("===== GENERATED SQL =====")
print(sql)


# 2. Validate SQL
is_safe, message = validate_sql(sql)

print("\n===== VALIDATION =====")
print("Safe:", is_safe)
print("Message:", message)


# 3. Execute only if safe
if is_safe:
    results = execute_sql(sql)

    print("\n===== DATABASE RESULT =====")

    for row in results:
        print(row)

else:
    print("\nSQL execution blocked!")