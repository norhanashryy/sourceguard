import os

from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()


def get_client():
    url = os.getenv("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")

    return QdrantClient(
        url=url,
        api_key=api_key,
    )