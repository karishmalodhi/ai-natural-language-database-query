from rag.knowledge import get_knowledge


def retrieve_context(question):
    knowledge = get_knowledge()

    question_words = question.lower().split()

    results = []

    for item in knowledge:
        text = item["text"].lower()

        score = 0

        for word in question_words:
            if word in text:
                score += 1

        if score > 0:
            results.append((score, item["text"]))

    results.sort(reverse=True)

    return [text for score, text in results]


if __name__ == "__main__":
    question = "Show me customers from Agra"

    results = retrieve_context(question)

    print("===== RETRIEVED CONTEXT =====")

    for result in results:
        print(result)