
import requests
from rag.retriever import retrieve_context


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.2:latest"


def ask_ollama(prompt):
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )
    response.raise_for_status()
    return response.json()["response"].strip()


def generate_sql(question, schema):
    context = retrieve_context(question)
    rag_context = "\n\n".join(context)

    prompt = f"""
You generate read-only PostgreSQL queries.

Knowledge:
{rag_context}

Schema:
{schema}

Question:
{question}

Rules:
- Return exactly one SELECT query.
- Use only schema tables and columns.
- Never generate a write or DDL operation.
- Return SQL only, without markdown or explanation.

SQL:
"""
    return ask_ollama(prompt)


def generate_sql_retry(question, schema, previous_query):
    context = retrieve_context(question)
    rag_context = "\n\n".join(context)

    prompt = f"""
Generate a corrected, read-only PostgreSQL SELECT query.

Knowledge:
{rag_context}

Schema:
{schema}

Question:
{question}

Rejected query:
{previous_query}

Rules:
- Return exactly one SELECT query.
- Use only tables and columns in the schema.
- Never use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE,
  TRUNCATE, or other write operations.
- Return SQL only, no markdown or explanation.

Corrected SQL:
"""
    return ask_ollama(prompt)


def generate_answer(question, results):
    question_lower = question.lower()

    count_phrases = (
        "how many",
        "count ",
        "number of",
        "total number",
        "total customers",
        "customer count"
    )

    is_count_question = any(
        phrase in question_lower
        for phrase in count_phrases
    )

    if is_count_question and isinstance(results, list):
        # PostgreSQL COUNT(*) returns one row containing the count.
        if (
            results
            and isinstance(results[0], dict)
            and "count" in results[0]
        ):
            count = results[0]["count"]
            return (
                f"There are {count} customers "
                "matching your question."
            )

        # MongoDB returns matching customer documents.
        return (
            f"There are {len(results)} customers "
            "matching your question."
        )

    prompt = f"""
You are a database assistant.

Question:
{question}

Actual database results:
{results}

Give a short, clear answer based only on these results.
Never invent facts or claim data that is not present.
Do not mention SQL or the database.
If the results are empty, say no matching data was found.

Answer:
"""
    return ask_ollama(prompt)


def generate_mongodb_query(question, schema):
    question_lower = question.lower()

    count_phrases = (
        "how many",
        "count ",
        "number of",
        "total number",
        "total customers",
        "customer count"
    )

    if any(phrase in question_lower for phrase in count_phrases):
        return "{}"

    context = retrieve_context(question)
    rag_context = "\n\n".join(context)

    prompt = f"""
Generate a MongoDB FILTER object for a read-only find() query.

Collection schema:
{schema}

Relevant knowledge:
{rag_context}

User question:
{question}

STRICT RULES:
- Return one valid JSON object only.
- Use only these fields: name, city, age, email.
- Use direct equality filters only.
- Do not use MongoDB operators or aggregation pipelines.
- Do not generate database commands or write operations.
- Never include fields with empty-string values.
- No markdown, comments, or explanations.

Examples:
Question: Show all customers.
Output: {{}}

Question: Show customers from Agra.
Output: {{"city": "Agra"}}

Question: Show customers from Delhi.
Output: {{"city": "Delhi"}}

Question: Find customers named Karishma.
Output: {{"name": "Karishma"}}

Question: Show customers aged 20.
Output: {{"age": 20}}

Return only the JSON filter:
"""
    return ask_ollama(prompt)


def generate_mongodb_query_retry(
    question,
    schema,
    previous_query
):
    question_lower = question.lower()

    count_phrases = (
        "how many",
        "count ",
        "number of",
        "total number",
        "total customers",
        "customer count"
    )

    if any(phrase in question_lower for phrase in count_phrases):
        return "{}"

    context = retrieve_context(question)
    rag_context = "\n\n".join(context)

    prompt = f"""
Correct the rejected MongoDB FILTER object.

Collection schema:
{schema}

Relevant knowledge:
{rag_context}

Question:
{question}

Rejected output:
{previous_query}

Allowed fields: name, city, age, email.

Rules:
- Return exactly one valid JSON object.
- Use direct equality filters only.
- Never include empty-string values.
- For customers from Agra, return {{"city": "Agra"}}.
- Never use operators, aggregation pipelines, or write commands.
- Do not include markdown or explanations.

Corrected JSON filter:
"""
    return ask_ollama(prompt)
