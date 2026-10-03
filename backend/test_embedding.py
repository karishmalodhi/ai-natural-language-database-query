from fastembed import TextEmbedding

model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

text = "Show me all customers from Agra"

embedding = list(model.embed([text]))[0]

print("Embedding generated!")
print("Vector length:", len(embedding))
print("First 10 values:", embedding[:10])