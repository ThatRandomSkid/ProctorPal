import openai
from Vectors.Vectors_Hidden import YOUR_API_KEY
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI


oclient = OpenAI(api_key=YOUR_API_KEY)

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
    
    def filtering(response):
        split_response = str(response).split(":")
        split_response = str(split_response[1]).split("}")
        return split_response[0]
    
    
    filtered = ["1","2","3","4","5"]

    for i in range(5):
        filtered[i] = filtering(str(database_response[i]))
        print(str(i+1)+".", filtered[i], "\n")


    messages = [{"role": "system", "content": "You are an assistent designed to answer questions about Proctor Academy. Do not halucinate responses. Make sure all responses look natural, no Answer: or Query:. DO NOT include information irrelevent to the question, even if it is given to you."}]
    
    messages.append({"role": "user", "content": str(filtered)})

    chat = oclient.chat.completions.create(
        model="gpt-3.5-turbo", messages=messages
    )
      
    reply = chat.choices[0].message.content
    print(f"ProctorPal: {reply}")
    messages.append({"role": "assistant", "content": reply})
