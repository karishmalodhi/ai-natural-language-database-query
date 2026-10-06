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
        Example cities in the current dataset include Agra, Delhi,
        Mumbai, and Jaipur.
        """
    },

    {
        "text": """
        The age field represents the customer's age.
        It is stored as an integer.
        """
    },

    {
        "text": """
        The name field represents the customer's name.
        """
    },

    {
        "text": """
        The email field represents the customer's email address.
        Email is sensitive personal information and should not be
        unnecessarily exposed in responses.
        """
    },

    {
        "text": """
        Questions asking how many customers exist should use a
        COUNT operation in PostgreSQL or an equivalent read-only
        MongoDB query.
        """
    },

    {
        "text": """
        Questions asking for customers from a particular city
        should use the city field as a filter.
        Example: customers from Agra means city = Agra.
        """
    },

    {
        "text": """
        Questions asking for customer names should use the name field.
        If the question is a follow-up such as "What are their names?",
        use the previous conversation context to understand which
        customers are being referenced.
        """
    },

    {
        "text": """
        The database system is read-only.
        Queries must only retrieve information.
        INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, and TRUNCATE
        operations are not allowed.
        """
    }

]


def get_knowledge():
    return DATABASE_KNOWLEDGE


if __name__ == "__main__":

    for item in DATABASE_KNOWLEDGE:

        print(item["text"])