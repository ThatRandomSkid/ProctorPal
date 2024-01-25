import openai
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.http.models import PointStruct
import numpy as np
from langchain_openai import OpenAIEmbeddings
import json



client = QdrantClient("localhost", port=6333)

client.create_collection(
    collection_name="test_collection7",
    vectors_config=VectorParams(size=1536, distance=Distance.DOT),
)