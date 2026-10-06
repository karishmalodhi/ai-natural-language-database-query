import requests

from rag.retriever import retrieve_context


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:latest"


def generate_sql(question, schema):

    context = retrieve_context(question)

    rag_context = "\n\n".join(context)

    prompt = f"""
You are a PostgreSQL SQL query generator.

Relevant database knowledge:
{rag_context}

Database schema:
{schema}

User question:
{question}

Rules:
- Generate ONLY a PostgreSQL SELECT query.
- Never generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, or TRUNCATE.
- Use only tables and columns present in the schema.
- Use the relevant database knowledge when generating the query.
- Return ONLY the SQL query.
- Do not add explanation or markdown.

SQL:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    response.raise_for_status()

    result = response.json()

    return result["response"].strip()


def generate_answer(question, results):

    prompt = f"""
You are a helpful database assistant.

User question:
{question}

Database result:
{results}

Give a short, clear, human-readable answer based ONLY on the database result.

Rules:
- Do not invent any information.
- Do not mention SQL.
- Do not mention the database.
- Answer directly.
- If the result is a count, clearly state the count.

Answer:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    response.raise_for_status()

    result = response.json()

    return result["response"].strip()


def generate_mongodb_query(question, schema):

    context = retrieve_context(question)

    rag_context = "\n\n".join(context)

    prompt = f"""
You are a MongoDB query generator.

Relevant database knowledge:
{rag_context}

MongoDB collection schema:
{schema}

User question:
{question}

Rules:
- Generate ONLY a MongoDB filter object.
- Use only fields present in the schema.
- Do not use insert, update, delete, drop, or any write operation.
- Use the relevant database knowledge when generating the query.
- Return ONLY valid JSON.
- Do not add explanation.
- Do not use markdown.

MongoDB filter:
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    response.raise_for_status()

    result = response.json()

    return result["response"].strip()