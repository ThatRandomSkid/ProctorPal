import os
from Vectors.Hidden import YOUR_API_KEY
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
import json
import streamlit as st
import time

"""# ProctorPal"""

# Initialize clients
embeddings_model = OpenAIEmbeddings(openai_api_key=(os.getenv("YOUR_API_KEY")))
oclient = OpenAI(api_key=YOUR_API_KEY)
qclient = QdrantClient("localhost", port=6333)

# Initilize lists/variables
parsed = ["1","2","3","4","5"]

# Gets user input from site 
query = st.text_input("User: ")

# Holds program until user enters text
while query == '':
    time.sleep(0.1)

# Querys database
embedded_query = embeddings_model.embed_query(query)

# Get database output
database_response = qclient.search( 
    collection_name="test_collection4", query_vector=embedded_query, limit=5
)

# Gives ChatGPT api input
messages = [{"role": "system", "content": "You are an assistent designed to answer questions about Proctor Academy. Here is the user question: " + query}]
messages.append({"role": "user", "content": str(database_response)})

chat = oclient.chat.completions.create(
    model="gpt-3.5-turbo", messages=messages
)

# Gets ChatGPT api response
reply = chat.choices[0].message.content
st.write(f"ProctorPal: {reply}")
