from sqlalchemy import create_engine


# ==========================================
# READ-ONLY POSTGRESQL CONNECTION
# ==========================================

DATABASE_URL = (
    "postgresql+pg8000://"
    "ai_readonly:AI_ReadOnly_2026"
    "@localhost:5432/ai_query_db"
)


engine = create_engine(
    DATABASE_URL
)


print(
    "Read-only PostgreSQL connection setup ready!"
)


# ==========================================
# TEST DATABASE CONNECTION
# ==========================================

try:

    with engine.connect() as connection:

        print(
            "PostgreSQL read-only connection successful!"
        )

except Exception as e:

    print(
        "PostgreSQL connection failed:",
        e
    )