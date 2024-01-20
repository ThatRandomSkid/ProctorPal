import openai
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.http.models import PointStruct
from Hidden import Qdrant_API_KEY
import numpy as np
from Hidden import YOUR_API_KEY
from langchain_openai import OpenAIEmbeddings
import json


client = QdrantClient("localhost", port=6333)

client.create_collection(
    collection_name="test_collection4",
    vectors_config=VectorParams(size=1536, distance=Distance.DOT),
)