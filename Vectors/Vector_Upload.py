import openai
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.http.models import PointStruct
import numpy as np
from langchain_openai import OpenAIEmbeddings
import json
import os
from dotenv import load_dotenv


YOUR_API_KEY = os.getenv("YOUR_API_KEY")

client = QdrantClient("localhost", port=6333)

embeddings_model = OpenAIEmbeddings(openai_api_key = YOUR_API_KEY)

n = 0

with open('Data/Training_Data/handbook_output.txt', 'r') as f:
    text = f.read()
    text2 = text.split(".")

while(n != len(text2)):
    embedded_query = embeddings_model.embed_query(text2[n])

    print(n)
    print(text2[n])
    
    operation_info = client.upsert(
        collection_name="test_collection7",
        wait=True,
        points=[
            PointStruct(id=(n), vector=embedded_query, payload={"input": text2[n]}),
        ],

    )

    n = n + 1


