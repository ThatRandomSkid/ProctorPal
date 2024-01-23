import os
import openai
from Hidden import YOUR_API_KEY
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
import json


# Initialize clients
embeddings_model = OpenAIEmbeddings(openai_api_key=YOUR_API_KEY)
oclient = OpenAI(api_key=YOUR_API_KEY)
qclient = QdrantClient("localhost", port=6333)


# Initilize lists
history = ["1","2","3"]
parsed = ["1","2","3","4","5"]

# Main loop
while True:
    query = input("User: ")
    
    # Break case
    if query.lower() == "stop":  
        break

    # Querys database
    embedded_query = embeddings_model.embed_query(query)
    
    # Get database output
    database_response = qclient.search( 
        collection_name="test_collection4", query_vector=embedded_query, limit=5
    )
    print(type(database_response))
    # Parses JSON response from database
    for i in range(5):
        parsed[i] = json.loads(str(database_response[i]))
        parsed[i] = parsed[i]["payload"]['input']

    # Gives ChatGPT api input
    messages = [{"role": "system", "content": "You are an assistent designed to answer questions about Proctor Academy."}]
    messages.append({"role": "user", "content": str(parsed)})
    messages.append({"chat_history": "Here is the chat history: " + str(history) + " Refer to this information is the user asks follow up questions."})

    chat = oclient.chat.completions.create(
        model="gpt-3.5-turbo", messages=messages
    )

    # Gets ChatGPT api response
    reply = chat.choices[0].message.content
    print(f"ProctorPal: {reply}")

    print(messages)

    # Resets history list
    for i in range(2):
        
        history[0] = ("User input", i+1, "question[s] ago:", query , "Your response", i+1, "question[s] ago:", reply )

        if i < 2:
            history[i+1] = history[i]
        else:
            break