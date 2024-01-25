import openai
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.http.models import PointStruct
import numpy as np
from langchain_openai import OpenAIEmbeddings
import json
import os

client = QdrantClient("localhost", port=6333)

embeddings_model = OpenAIEmbeddings(openai_api_key=(os.getenv("YOUR_API_KEY")))

n = 0

openai_api_key = os.getenv("YOUR_API_KEY")

with open('Vectors/handbook_output.txt', 'r') as f:
    text = f.read()
    text2 = text.split(".")


while(n != len(text2)):
    embedded_query = embeddings_model.embed_query(text2[n])
    embedded_query[:5]

    print(n)
    print(text2[n])
    
    url = f"http://localhost:6333/collections/{'test_collection5'}/points"
    headers = {'Content-Type': 'application/json'}
    data = {
        "ids": [n],
        "vectors": [embedded_query],
        "payload": text2[n]
    }

    n = n + 1

print(data)

