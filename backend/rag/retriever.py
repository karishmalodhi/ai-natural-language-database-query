import math
import re

from rag.knowledge import get_knowledge


# ==========================================
# LOAD KNOWLEDGE BASE
# ==========================================

knowledge = get_knowledge()

knowledge_texts = [
    item["text"]
    for item in knowledge
]


# ==========================================
# TEXT PREPROCESSING
# ==========================================

def tokenize(text):

    text = text.lower()

    words = re.findall(
        r"[a-zA-Z0-9_]+",
        text
    )

    return words


# ==========================================
# BUILD VOCABULARY
# ==========================================

vocabulary = set()

for text in knowledge_texts:

    vocabulary.update(
        tokenize(text)
    )

vocabulary = sorted(vocabulary)


word_to_index = {
    word: index
    for index, word in enumerate(vocabulary)
}


# ==========================================
# CREATE TEXT VECTOR
# ==========================================

def create_vector(text):

    words = tokenize(text)

    vector = [0] * len(vocabulary)

    for word in words:

        if word in word_to_index:

            index = word_to_index[word]

            vector[index] += 1

    return vector


# ==========================================
# CREATE KNOWLEDGE VECTORS
# ==========================================

knowledge_vectors = [
    create_vector(text)
    for text in knowledge_texts
]


# ==========================================
# COSINE SIMILARITY
# ==========================================

def cosine_similarity(vector_a, vector_b):

    dot_product = 0
    magnitude_a = 0
    magnitude_b = 0

    for a, b in zip(vector_a, vector_b):

        dot_product += a * b

        magnitude_a += a * a

        magnitude_b += b * b

    magnitude_a = math.sqrt(magnitude_a)

    magnitude_b = math.sqrt(magnitude_b)

    if magnitude_a == 0 or magnitude_b == 0:

        return 0.0

    return (
        dot_product
        / (magnitude_a * magnitude_b)
    )


# ==========================================
# VECTOR RAG RETRIEVER
# ==========================================

def retrieve_context(question, top_k=5):

    question_vector = create_vector(
        question
    )

    scored_results = []

    for index, knowledge_vector in enumerate(
        knowledge_vectors
    ):

        score = cosine_similarity(
            question_vector,
            knowledge_vector
        )

        scored_results.append(
            (
                score,
                knowledge_texts[index]
            )
        )

    # Highest similarity first
    scored_results.sort(
        key=lambda item: item[0],
        reverse=True
    )

    results = []

    for score, text in scored_results[:top_k]:

        # Ignore completely unrelated knowledge
        if score > 0:

            results.append(text)

    return results


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    questions = [
        "Show me customers from Agra",
        "How many customers are there?",
        "What is the age of the customer?",
        "What are their names?"
    ]

    for question in questions:

        print("\n===================================")
        print("QUESTION:", question)
        print("===================================")

        results = retrieve_context(question)

        for result in results:

            print("\n", result)