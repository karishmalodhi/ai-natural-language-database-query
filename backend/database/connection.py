import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

user = quote_plus(os.environ["POSTGRES_USER"])
password = quote_plus(os.environ["POSTGRES_PASSWORD"])
host = os.getenv("POSTGRES_HOST", "localhost")
port = os.getenv("POSTGRES_PORT", "5432")
database = os.getenv("POSTGRES_DB", "ai_query_db")

DATABASE_URL = (
    f"postgresql+pg8000://{user}:{password}"
    f"@{host}:{port}/{database}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

print("Read-only PostgreSQL connection setup ready!")

try:
    with engine.connect() as connection:
        print("PostgreSQL connection successful!")
except Exception as e:
    print("PostgreSQL connection failed:", e)