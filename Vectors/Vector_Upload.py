from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
import os
from dotenv import load_dotenv


load_dotenv()
os.environ["OPENAI_API_KEY"]

context = ""
oclient = OpenAI()
qclient = QdrantClient("localhost", port=6333)

n = 0

with open('Training_Data/handbook_output.txt', 'r') as f:
    text = f.read()
    text2 = text.split(".")

while(n != len(text2)):
    text2[n] = context + text2[n]
    
    embedded_query = oclient.embeddings.create(input = [text2[n]], model="text-embedding-3-large").data[0].embedding


    print(n)
    print(text2[n])
    
    operation_info = qclient.upsert(
        collection_name="test_collection11",
        wait=True,
        points=[
            PointStruct(id=(n), vector=embedded_query, payload={"input": text2[n]}),
        ],

    )

    n = n + 1


