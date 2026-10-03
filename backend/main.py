from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.llm_service import generate_sql
from database.utils.sql_validator import validate_sql
from services.db_service import execute_sql


app = FastAPI()


# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str


schema = """
customers(
    id INTEGER,
    name VARCHAR(100),
    city VARCHAR(100),
    age INTEGER,
    email VARCHAR(150)
)
"""


@app.get("/")
def home():
    return {
        "message": "AI Database Query System is running!"
    }


@app.post("/chat")
def chat(request: ChatRequest):

    # Generate SQL
    sql = generate_sql(request.question, schema)

    # Validate SQL
    is_safe, message = validate_sql(sql)

    if not is_safe:
        return {
            "success": False,
            "error": message
        }

    # Execute SQL
    try:
        results = execute_sql(sql)

        return {
            "success": True,
            "question": request.question,
            "sql": sql,
            "results": results
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }