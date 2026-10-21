from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from datetime import datetime

from services.llm_service import (
    generate_sql,
    generate_sql_retry,
    generate_mongodb_query,
    generate_mongodb_query_retry,
    generate_answer
)

from database.utils.sql_validator import validate_sql
from services.db_service import execute_sql
from services.mongodb_service import (
    execute_mongodb_query,
    validate_mongodb_query
)


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

    database: str = "auto"

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


# ==========================================
# CLARIFICATION HANDLING
# ==========================================

def needs_clarification(question):

    normalized = question.lower().strip()

    ambiguous_questions = {

        "show customers",
        "show me customers",
        "give me customers",
        "tell me about customers",
        "customers",
        "show customer",
        "show me customer",
        "give me customer",
        "customer details",
        "show customer details",
        "show me customer details"
    }

    return normalized in ambiguous_questions


def clarification_response():

    return {

        "success": True,

        "clarification_required": True,

        "message": (
            "Could you specify what customer information "
            "you want? For example, you can ask for customers "
            "from a particular city, customer names, or customer ages."
        )
    }


# ==========================================
# CLEAN SQL RESPONSE
# ==========================================

def clean_sql(sql):

    sql = sql.replace(
        "```sql",
        ""
    )

    sql = sql.replace(
        "```",
        ""
    )

    return sql.strip()


# ==========================================
# CLEAN MONGODB RESPONSE
# ==========================================

def clean_mongodb_response(query):

    query = query.replace(
        "```json",
        ""
    )

    query = query.replace(
        "```",
        ""
    )

    return query.strip()


# ==========================================
# HOME
# ==========================================

@app.get("/")
def home():

    return {

        "message":
        "AI Database Query System is running!"
    }


# ==========================================
# CHAT
# ==========================================

@app.post("/chat")
def chat(request: ChatRequest):

    try:

        # ==================================
        # BASIC QUESTION VALIDATION
        # ==================================

        if not request.question.strip():

            return {

                "success": False,

                "error":
                "Please enter a question."
            }
        # Block write or destructive requests
        question_lower = request.question.lower()

        dangerous_terms = (
            "delete", "drop", "truncate",
            "update", "insert", "remove", "alter"
        )

        if any(term in question_lower for term in dangerous_terms):
            return {
                "success": False,
                "error": "Write operations are not allowed. This system is read-only."
            }

        # Automatic database selection
        selected_database = request.database.lower().strip()

        if selected_database == "auto":
            if "mongo" in question_lower:
                selected_database = "mongodb"
            else:
                selected_database = "postgresql"

        # ==================================
        # CLARIFICATION CHECK
        # ==================================

        if needs_clarification(
            request.question
        ):

            return clarification_response()


        # ==================================
        # CONVERSATION CONTEXT
        # ==================================

        conversation_context = ""

        if request.conversation:

            conversation_context = (
                "\nPrevious conversation:\n"
            )

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


        # ==================================
        # MONGODB
        # ==================================

        if selected_database == "mongodb":

            mongo_question = (

                conversation_context
                + "\nCurrent user question:\n"
                + request.question
            )


            # ----------------------------------
            # FIRST AI QUERY
            # ----------------------------------

            mongo_query_text = generate_mongodb_query(

                mongo_question,

                mongodb_schema
            )

            mongo_query_text = clean_mongodb_response(
                mongo_query_text
            )


            try:

                mongo_query = json.loads(
                    mongo_query_text
                )

            except json.JSONDecodeError:

                mongo_query = None


            # ----------------------------------
            # VALIDATE FIRST QUERY
            # ----------------------------------

            if mongo_query is not None:

                mongo_safe, mongo_message = (
                    validate_mongodb_query(
                        mongo_query
                    )
                )

            else:

                mongo_safe = False

                mongo_message = (
                    "Invalid MongoDB JSON query."
                )


            # ----------------------------------
            # SAFE RETRY
            # ----------------------------------

            if not mongo_safe:

                mongo_query_text = (
                    generate_mongodb_query_retry(

                        mongo_question,

                        mongodb_schema,

                        mongo_query_text
                    )
                )

                mongo_query_text = (
                    clean_mongodb_response(
                        mongo_query_text
                    )
                )


                try:

                    mongo_query = json.loads(
                        mongo_query_text
                    )

                except json.JSONDecodeError:

                    mongo_query = None


                if mongo_query is not None:

                    mongo_safe, mongo_message = (
                        validate_mongodb_query(
                            mongo_query
                        )
                    )

                else:

                    mongo_safe = False

                    mongo_message = (
                        "Invalid MongoDB query after safe retry."
                    )


            # ----------------------------------
            # RETRY FAILED
            # ----------------------------------

            if not mongo_safe:

                write_audit_log(

                    request.question,

                    "mongodb",

                    mongo_query_text,

                    0,

                    False
                )

                return {

                    "success": False,

                    "error":
                    "AI could not generate a safe MongoDB query after one retry."
                }


            # ----------------------------------
            # EXECUTE SAFE QUERY
            # ----------------------------------

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


        # ==================================
        # POSTGRESQL
        # ==================================

        sql_question = (

            conversation_context
            + "\nCurrent user question:\n"
            + request.question
        )


        # ----------------------------------
        # FIRST AI QUERY
        # ----------------------------------

        sql = generate_sql(

            sql_question,

            sql_schema
        )

        sql = clean_sql(sql)


        # ----------------------------------
        # VALIDATE FIRST QUERY
        # ----------------------------------

        is_safe, message = validate_sql(sql)


        # ----------------------------------
        # SAFE RETRY
        # ----------------------------------

        if not is_safe:

            retry_sql = generate_sql_retry(

                sql_question,

                sql_schema,

                sql
            )

            retry_sql = clean_sql(
                retry_sql
            )

            retry_safe, retry_message = (
                validate_sql(
                    retry_sql
                )
            )


            if retry_safe:

                sql = retry_sql

                is_safe = True

            else:

                write_audit_log(

                    request.question,

                    "postgresql",

                    retry_sql,

                    0,

                    False
                )

                return {

                    "success": False,

                    "error":
                    "AI could not generate a safe SQL query after one retry."
                }


        # ----------------------------------
        # EXECUTE SAFE SQL
        # ----------------------------------

        results = execute_sql(sql)


        # ----------------------------------
        # GENERATE ANSWER
        # ----------------------------------

        answer = generate_answer(

            request.question,

            results
        )


        # ----------------------------------
        # AUDIT SUCCESS
        # ----------------------------------

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


    # ======================================
    # INVALID MONGODB JSON
    # ======================================

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

            "error":
            "Invalid MongoDB query generated by AI."
        }


    # ======================================
    # GENERAL ERROR
    # ======================================

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