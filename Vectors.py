from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from qdrant_client.http.models import Distance, VectorParams
import os
from dotenv import load_dotenv


# Editable variables
database_name = "db3"
database_ip = "localhost"
n = 0
data_file_name = 'bot_description.txt'
context = ""

# Determine if user wants to create a new database or not
create_new = input("Create new database? y/n: ")
if create_new.lower == "y":
    database_name = input("New databsebase name:")



# Load OpenAI API key form .env
load_dotenv()
os.environ["OPENAI_API_KEY"]

# Inizalize clients
oclient = OpenAI()
qclient = QdrantClient(database_ip, port=6333)

# Create new database if specified
if create_new == "y":
    oclient.create_collection(
        collection_name= database_name,
        vectors_config=VectorParams(size=3072, distance=Distance.DOT),
    )

# Sets file path
file_path = os.path.expanduser(f'~/ProctorPal/Training_Data/{data_file_name}')

# Chunking
with open(file_path, 'r') as f:
    text = f.read()
    text2 = text.split(".")

# Vector embedding/upload loop
while(n != len(text2)):

    # Prints values for debugging
    print(n)
    print(text2[n])

    # Adds context if specified
    if context != "":
        text2[n] = context + text2[n] 
    
    # Embedding function
    embedded_query = oclient.embeddings.create(input = [text2[n]], model="text-embedding-3-large").data[0].embedding
    
    # Vector uplaod
    operation_info = qclient.upsert(
        collection_name=database_name,
        wait=True,
        points=[
            PointStruct(id=(n), vector=embedded_query, payload={"input": text2[n]}),
        ],

    )
    
    # Iterates loop
    n = n + 1