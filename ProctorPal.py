import os
import openai
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
import json
import streamlit as st
import time
from dotenv import load_dotenv

# Webpage design
"""# ProctorPal"""

# Import OpenAI api key from .env
load_dotenv()
YOUR_API_KEY = os.getenv("YOUR_API_KEY")

# Initialize clients
embeddings_model = OpenAIEmbeddings(openai_api_key=YOUR_API_KEY)
oclient = OpenAI(api_key=YOUR_API_KEY)
qclient = QdrantClient("localhost", port=6333)

# Initilize lists/variables
filtered = ["1","2","3","4","5"]

# Gets user input from site 
query = st.text_input("User: ")

# Holds program until user enters text
while query == '':
    time.sleep(0.1)

# Querys database
embedded_query = embeddings_model.embed_query(query)
embedded_query[:5]

# Get database output
database_response = qclient.search( 
    collection_name="test_collection4", query_vector=embedded_query, limit=5
)

# Filter database response (replace with valid json implimentation eventually)
def filtering(response):
    split_response = str(response).split(":")
    split_response = str(split_response[1]).split("}")
    print(str(i+1)+".", split_response, "\n")
    return split_response[0].replace("\n", "")

for i in range(5):
    filtered[i] = filtering(str(database_response[i]))
    print(str(i+1)+".", filtered[i], "\n")

# Gives ChatGPT api input
messages = [{"role": "system", "content": "You are an assistent designed to answer questions about Proctor Academy. Here is the user question: " + query}]
messages.append({"role": "user", "content": str(filtered)})

chat = oclient.chat.completions.create(
    model="gpt-3.5-turbo", messages=messages
)

# Gets ChatGPT api response
reply = chat.choices[0].message.content
st.write(f"ProctorPal: {reply}")
