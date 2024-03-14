from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from qdrant_client.http.models import Distance, VectorParams
import os
from dotenv import load_dotenv
import json
import time


# Editable variables
data_file_name = 'bot_description.txt'
context = ""
n = 0
retry_times = 20

# Gets settings from settings.json file
settings_path = os.path.expanduser("~/ProctorPal/settings.json")
with open(settings_path, 'r') as f:
    d = json.load(f)
    database_ip = d.get("database_ip")
    database_name = d.get("database_name")

# Determine if user wants to create a new database or not
create_new = input("Create new database? y/n: ")
if create_new == "y":
    database_name = input("New databsebase name: ")
    with open(settings_path, 'r') as f:
        d = json.load(f)
        d["database_name"] = database_name
    with open(settings_path, 'w') as f:
        json.dump(d, f, indent=4)
elif create_new != "n":
    print("Input is invalid. Please try again.")
    exit()

# Determine data to upload
data_file_name = input("What is the name of the file that the data you want to upload is in? ")

# Determine chuncking method
chunking_method = input('What chuncking method should be used? Type "n" for new line character split (\\n), "s" for sentence split (.) or "p" for paragraph split (\\n\\\n): ')



# Sets chunking method
if chunking_method == "n":
    divider = "\\n"
elif chunking_method == "s":
    divider = "."
elif chunking_method == "p":
    divider = "\n\n"
else: 
    print("Input is invalid. Please try again.")
    exit()

# Load OpenAI API key form .env
load_dotenv()
os.environ["OPENAI_API_KEY"]

# Inizalize clients
oclient = OpenAI()
qclient = QdrantClient(database_ip, port=6333)

# Create new database if specified
if create_new == "y":
    qclient.create_collection(
        collection_name= database_name,
        vectors_config=VectorParams(size=3072, distance=Distance.DOT),
    )

# Sets file path
file_path = os.path.expanduser(f'~/ProctorPal/Training_Data/{data_file_name}')

# Opens the file data is in
file = open(file_path, 'r')

# Finds file type
file_type = data_file_name.split(".")

# Loads data from context file
if file_type[1] == "txt" or file_type[1] == "cvs": 
    text = file.read()
elif file_type[1] == "json":
    f = json.load(file)
    text = [item.get('text') for item in f]
    text = str(text)
else:
    print("File extention is invalid. Please try again.")
    exit()

# Chunking
text2 = text.split(divider)

# Function for vector embedding/uploading
def vector_upload(text2, database_name, context):
    global n # Declare n as global
    try:
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
            n += 1
        # Exit statement upon success
        print("Finished")
        return None, None
    
    except Exception as e: 
        print(f"Attempt failed: {e}.")
        return n, e


# Handles errors
for i in range(retry_times):
    result, e = vector_upload(text2, database_name, context)
    if result == None:
        break
    else:
        time.sleep(3)
        n = result
        e = str(e)
        if "400" in e:
            n += 1