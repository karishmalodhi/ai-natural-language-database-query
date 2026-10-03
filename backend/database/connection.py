from sqlalchemy import create_engine
DATABASE_URL = "postgresql+pg8000://postgres:8923484740@localhost:5432/ai_query_db"

engine = create_engine(DATABASE_URL)

print("Database connection setup ready!")
try:
    with engine.connect() as connection:
        print("PostgreSQL connected successfully!")
except Exception as e:
    print("Connection failed:", e)