from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from datetime import datetime

from services.llm_service import (
    generate_sql,
    generate_mongodb_query,
    generate_answer
)

from database.utils.sql_validator import validate_sql
from services.db_service import execute_sql
from services.mongodb_service import execute_mongodb_query


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str
    database: str = "postgresql"
    conversation: list = []


sql_schema = """
customers(
    id INTEGER,
    name VARCHAR(100),
    city VARCHAR(100),
    age INTEGER,
    email VARCHAR(150)
)
"""


mongodb_schema = """
customers(
    name STRING,
    city STRING,
    age INTEGER,
    email STRING
)
"""


# ==========================================
# AUDIT LOG
# ==========================================

def write_audit_log(
    question,
    database,
    query,
    result_count,
    success
):

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "database": database,
        "query": query,
        "result_count": result_count,
        "success": success
    }

    with open(
        "audit.log",
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            json.dumps(log_entry)
            + "\n"
        )


@app.get("/")
def home():

    return {
        "message": "AI Database Query System is running!"
    }


@app.post("/chat")
def chat(request: ChatRequest):

    try:

        # ==========================================
        # BUILD CONVERSATION CONTEXT
        # ==========================================

        conversation_context = ""

        if request.conversation:

            conversation_context = "\nPrevious conversation:\n"

            for item in request.conversation[-5:]:

                conversation_context += (
                    f"\nPrevious User Question:\n"
                    f"{item.get('question', '')}\n"
                )

                conversation_context += (
                    f"Previous Generated Query:\n"
                    f"{item.get('query', '')}\n"
                )

                conversation_context += (
                    f"Previous Database Result:\n"
                    f"{json.dumps(item.get('results', []), indent=2)}\n"
                )

                conversation_context += (
                    f"Previous Answer:\n"
                    f"{item.get('answer', '')}\n"
                )

            conversation_context += (
                "\nEnd of previous conversation.\n"
            )


        # ==========================================
        # MONGODB FLOW
        # ==========================================

        if request.database.lower() == "mongodb":

            mongo_question = (
                conversation_context
                + "\nCurrent user question:\n"
                + request.question
            )

            mongo_query_text = generate_mongodb_query(
                mongo_question,
                mongodb_schema
            )

            mongo_query_text = mongo_query_text.replace(
                "```json",
                ""
            )

            mongo_query_text = mongo_query_text.replace(
                "```",
                ""
            )

            mongo_query_text = mongo_query_text.strip()

            mongo_query = json.loads(
                mongo_query_text
            )

            results = execute_mongodb_query(
                mongo_query
            )

            answer = generate_answer(
                request.question,
                results
            )

            write_audit_log(
                request.question,
                "mongodb",
                mongo_query,
                len(results),
                True
            )

            return {
                "success": True,
                "database": "mongodb",
                "question": request.question,
                "query": mongo_query,
                "results": results,
                "answer": answer
            }


        # ==========================================
        # POSTGRESQL FLOW
        # ==========================================

        sql_question = (
            conversation_context
            + "\nCurrent user question:\n"
            + request.question
        )

        sql = generate_sql(
            sql_question,
            sql_schema
        )

        sql = sql.replace(
            "```sql",
            ""
        )

        sql = sql.replace(
            "```",
            ""
        )

        sql = sql.strip()

        is_safe, message = validate_sql(sql)

        if not is_safe:

            write_audit_log(
                request.question,
                "postgresql",
                sql,
                0,
                False
            )

            return {
                "success": False,
                "error": message
            }

        results = execute_sql(sql)

        answer = generate_answer(
            request.question,
            results
        )

        write_audit_log(
            request.question,
            "postgresql",
            sql,
            len(results),
            True
        )

        return {
            "success": True,
            "database": "postgresql",
            "question": request.question,
            "sql": sql,
            "results": results,
            "answer": answer
        }


    except json.JSONDecodeError:

        write_audit_log(
            request.question,
            request.database,
            "Invalid JSON query",
            0,
            False
        )

        return {
            "success": False,
            "error": "Invalid MongoDB query generated by AI."
        }


    except Exception as e:

        write_audit_log(
            request.question,
            request.database,
            "Query execution failed",
            0,
            False
        )

        return {
            "success": False,
            "error": str(e)
        }