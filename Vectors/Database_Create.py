from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams


client = QdrantClient("localhost", port=6333)

client.create_collection(
    collection_name="newline_collection1",
    vectors_config=VectorParams(size=3072, distance=Distance.DOT),
)