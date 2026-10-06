from rag.knowledge import get_knowledge


def retrieve_context(question):
    knowledge = get_knowledge()

    question_words = question.lower().split()

    # Common words that do not help in finding relevant knowledge
    stop_words = {
        "what",
        "is",
        "are",
        "the",
        "a",
        "an",
        "how",
        "many",
        "me",
        "show",
        "tell",
        "give",
        "from",
        "of",
        "to",
        "in",
        "on",
        "for",
        "customers",
        "customer"
    }

    useful_words = [
        word.strip("?,.!'\"")
        for word in question_words
        if word.strip("?,.!'\"") not in stop_words
    ]

    results = []

    for item in knowledge:

        text = item["text"]
        text_lower = text.lower()

        score = 0

        for word in useful_words:

            if word in text_lower:
                score += 1

        if score > 0:
            results.append((score, text))

    # Highest relevance first
    results.sort(key=lambda x: x[0], reverse=True)

    return [text for score, text in results]


if __name__ == "__main__":

    question = "Show me customers from Agra"

    results = retrieve_context(question)

    print("===== RETRIEVED CONTEXT =====")

    for result in results:
        print(result)