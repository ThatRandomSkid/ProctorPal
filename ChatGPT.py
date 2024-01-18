import openai
from Vectors.Vectors_Hidden import YOUR_API_KEY
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings

# Set API key for OpenAI
openai.api_key = YOUR_API_KEY

# Initialize clients
embeddings_model = OpenAIEmbeddings(openai_api_key=YOUR_API_KEY)
qclient = QdrantClient("localhost", port=6333)

while True:  # Use 'True' for an infinite loop
    query = input("User: ")
    
    if query.lower() == "stop":  # Added lower() to handle different case inputs
        break

    embedded_query = embeddings_model.embed_query(query)
    
    database_response = qclient.search(
        collection_name="test_collection4", query_vector=embedded_query, limit=5
    )

    messages = [{"role": "system", "content": "You are designed to assist Proctor Students."}]
    
    messages.append({"role": "user", "content": str(database_response)})

    chat = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages
    )
      
    reply = chat.choices[0].message.content
    print(f"ChatGPT: {reply}")
    messages.append({"role": "assistant", "content": reply})
