DATABASE_KNOWLEDGE = [
    {
        "text": """
        PostgreSQL database contains a customers table.
        The customers table has columns:
        id, name, city, age, email.
        """
    },
    {
        "text": """
        MongoDB database contains a customers collection.
        The customers collection has fields:
        _id, name, city, age, email.
        """
    },
    {
        "text": """
        The city field represents the customer's city.
        The age field represents the customer's age.
        The name field represents the customer's name.
        """
    }
]


def get_knowledge():
    return DATABASE_KNOWLEDGE


if __name__ == "__main__":
    for item in DATABASE_KNOWLEDGE:
        print(item["text"])