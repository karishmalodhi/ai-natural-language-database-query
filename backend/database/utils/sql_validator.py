import re


DANGEROUS_KEYWORDS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "DROP",
    "ALTER",
    "CREATE",
    "TRUNCATE"
]


def validate_sql(sql):
    sql = sql.strip()

    # Only SELECT queries allowed
    if not sql.upper().startswith("SELECT"):
        return False, "Only SELECT queries are allowed."

    # Block dangerous SQL keywords
    for keyword in DANGEROUS_KEYWORDS:
        pattern = rf"\b{keyword}\b"

        if re.search(pattern, sql, re.IGNORECASE):
            return False, f"Dangerous SQL keyword detected: {keyword}"

    return True, "SQL is safe."