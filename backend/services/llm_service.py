import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:latest"


def generate_sql(question, schema):

    prompt = f"""
You are a PostgreSQL SQL query generator.

Database schema:
{schema}

User question:
{question}

Rules:
- Generate ONLY a PostgreSQL SELECT query.
- Never generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, or TRUNCATE.
- Use only tables and columns present in the schema.
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