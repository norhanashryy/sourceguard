from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from bs4 import SoupStrainer
import re
from langchain_ollama import OllamaEmbeddings
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from qdrant_client.models import PointStruct
import uuid



def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()
urls = [
    "https://docs.langchain.com/oss/python/langchain/overview",
    "https://docs.langchain.com/oss/python/langchain/retrieval",
    "https://docs.langchain.com/oss/python/langchain/knowledge-base",
    "https://docs.langchain.com/oss/python/langchain/agents",
    "https://docs.langchain.com/oss/python/langchain/tools",
    "https://docs.langchain.com/oss/python/langchain/models",
    "https://docs.langchain.com/oss/python/langgraph/agentic-rag",
        "https://qdrant.tech/documentation/guides/",
    "https://qdrant.tech/documentation/manage-data/collections/",
    "https://qdrant.tech/documentation/search/search/",
    "https://qdrant.tech/documentation/search/filtering/",
    "https://qdrant.tech/documentation/frameworks/langchain/",
]

loader = WebBaseLoader(urls,
    bs_kwargs={"parse_only": SoupStrainer("main")}
                       )
docs = loader.load()

for doc in docs:
    doc.page_content = clean_text(doc.page_content)

print(f"Documents: {len(docs)} ")#verifying
print("\nLoaded successfully!")
print("URL:", docs[0].metadata.get("source"))
print("Preview:", docs[0].page_content[:200].replace("\n", " ")) #checking contents

print("URL:", docs[1].metadata.get("source"))
print("Preview:", docs[1].page_content[:200].replace("\n", " "))

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)

chunks = text_splitter.split_documents(docs)

load_dotenv()

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

collection_name = "langchain_qdrant_docs"

if not client.collection_exists(collection_name):
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=768,
            distance=Distance.COSINE,
        ),
    )
    print(f"Created collection: {collection_name}")
else:
    print(f"Collection already exists: {collection_name}")

embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)

points = []

for chunk in chunks:
    vector = embeddings.embed_query(chunk.page_content)

    points.append(
        PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={
                "text": chunk.page_content,
                "source": chunk.metadata.get("source"),
            },
        )
    )

client.upsert(
    collection_name=collection_name,
    points=points,
)

print(f"Uploaded {len(points)} points to Qdrant")

for i, chunk in enumerate(chunks[:5]):
    print(f"\n--- CHUNK {i + 1} ---")
    print(chunk.page_content[:300])

print(f"Loaded {len(docs)} documents")
print(f"Created {len(chunks)} chunks")

test_embedding = embeddings.embed_query("What is LangChain?")
print(f"Embedding dimensions: {len(test_embedding)}")