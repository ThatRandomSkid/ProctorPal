import openai
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.http.models import PointStruct
from Vectors_Hidden import Qdrant_API_KEY
import numpy as np
from Vectors_Hidden import YOUR_API_KEY
from langchain_openai import OpenAIEmbeddings
import json

client = QdrantClient("localhost", port=6333)

embeddings_model = OpenAIEmbeddings(openai_api_key=YOUR_API_KEY)

n = 0

openai.api_key = YOUR_API_KEY

with open('Vectors/handbook_output.txt', 'r') as f:
    text = f.read()
    text2 = text.split(".")


while(n != len(text2)):
    embedded_query = embeddings_model.embed_query(text2[n])
    embedded_query[:5]

    print(n)
    print(text2[n])

    operation_info = client.upsert(
        collection_name="test_collection4",
        wait=True,
        points=[
            PointStruct(id=(n), vector=embedded_query, payload={"input": text2[n]}),
        ],

    )

    n = n + 1

print(operation_info)



