from langchain_ollama import OllamaEmbeddings
from qdrant import get_client

COLLECTION_NAME = "langchain_qdrant_docs"

client = get_client()

embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)

def search_docs(query, top_k= 5):
    queryVec = embeddings.embed_query(query)

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=queryVec,
        limit=top_k,
    )

    return results.points

if __name__ == "__main__":
    query = input("Ask a question: ")

    results = search_docs(query)

    print(f"\nFound {len(results)} results:\n")

    for i, result in enumerate(results, 1):
        print(f"--- Result {i} ---")
        print(f"Score: {result.score}")
        print(f"Source: {result.payload.get('source')}")
        print(f"Text: {result.payload.get('text')[:500]}")
        print()