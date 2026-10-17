
import math
import re
from collections import Counter

from rag.knowledge import get_knowledge


STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been",
    "am", "do", "does", "did", "how", "what", "which", "who",
    "where", "when", "why", "can", "could", "would", "should",
    "please", "me", "my", "i", "we", "you", "our", "to", "of",
    "in", "on", "at", "for", "from", "with", "and", "or", "by",
    "all", "show", "find", "get", "tell", "give", "list", "display"
}


def tokenize(text):
    """Convert text into useful searchable terms."""
    words = re.findall(r"[a-zA-Z0-9_]+", str(text).lower())

    # Keep meaningful words and normalize simple plurals.
    result = []
    for word in words:
        if word in STOPWORDS or len(word) < 2:
            continue

        if word.endswith("ies") and len(word) > 4:
            word = word[:-3] + "y"
        elif word.endswith("s") and not word.endswith("ss") and len(word) > 3:
            word = word[:-1]

        result.append(word)

    return result


def _get_chunks():
    """Support knowledge stored as text, a list, or dictionaries."""
    knowledge = get_knowledge()

    if isinstance(knowledge, str):
        return [knowledge] if knowledge.strip() else []

    if isinstance(knowledge, dict):
        knowledge = [knowledge]

    chunks = []

    if isinstance(knowledge, (list, tuple)):
        for item in knowledge:
            if isinstance(item, str):
                if item.strip():
                    chunks.append(item)
            elif isinstance(item, dict):
                text = item.get("content") or item.get("text")
                if text:
                    chunks.append(str(text))
                else:
                    chunks.append(
                        " ".join(f"{key}: {value}" for key, value in item.items())
                    )

    return chunks


def _vectorize(tokens, document_frequency, total_documents):
    """Create a TF-IDF vector using only Python's standard library."""
    counts = Counter(tokens)
    total_terms = max(len(tokens), 1)
    vector = {}

    for word, count in counts.items():
        tf = count / total_terms
        idf = math.log(
            (1 + total_documents) / (1 + document_frequency[word])
        ) + 1
        vector[word] = tf * idf

    return vector


def _cosine_similarity(first, second):
    """Measure similarity between two sparse TF-IDF vectors."""
    if not first or not second:
        return 0.0

    dot_product = sum(
        value * second.get(word, 0.0)
        for word, value in first.items()
    )

    first_norm = math.sqrt(sum(value * value for value in first.values()))
    second_norm = math.sqrt(sum(value * value for value in second.values()))

    if first_norm == 0 or second_norm == 0:
        return 0.0

    return dot_product / (first_norm * second_norm)


def retrieve_context(query, top_k=5):
    """
    Retrieve the most relevant knowledge chunks for a user question.
    Offline TF-IDF and cosine similarity; no external model required.
    """
    chunks = _get_chunks()

    if not chunks or not str(query).strip():
        return ""

    tokenized_chunks = [tokenize(chunk) for chunk in chunks]
    query_tokens = tokenize(query)

    if not query_tokens:
        return ""

    document_frequency = Counter()
    for tokens in tokenized_chunks:
        document_frequency.update(set(tokens))

    total_documents = len(chunks)

    query_vector = _vectorize(
        query_tokens, document_frequency, total_documents
    )

    ranked = []

    for index, tokens in enumerate(tokenized_chunks):
        document_vector = _vectorize(
            tokens, document_frequency, total_documents
        )

        score = _cosine_similarity(query_vector, document_vector)

        # Small bonus when an important query phrase occurs in a chunk.
        normalized_chunk = chunks[index].lower()
        normalized_query = str(query).lower().strip()

        if normalized_query and normalized_query in normalized_chunk:
            score += 0.15

        if score > 0:
            ranked.append((score, index, chunks[index]))

    ranked.sort(key=lambda item: item[0], reverse=True)

    limit = max(1, int(top_k))
    return "\n\n".join(item[2] for item in ranked[:limit])


if __name__ == "__main__":
    questions = [
        "What columns are in the customers table?",
        "Find customers from Agra",
        "How can I filter customers by age?",
        "What does the email field mean?",
    ]

    for question in questions:
        print(f"\nQuestion: {question}")
        context = retrieve_context(question)

        if context:
            print("Retrieved context:")
            print(context)
        else:
            print("No matching context found.")
