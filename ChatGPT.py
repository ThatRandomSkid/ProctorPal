import openai
from Vectors.Vectors_Hidden import YOUR_API_KEY
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI


oclient = OpenAI(api_key=YOUR_API_KEY)

# Initialize clients
embeddings_model = OpenAIEmbeddings(openai_api_key=YOUR_API_KEY)
qclient = QdrantClient("localhost", port=6333)

filtered = ["1","2","3","4","5"]
    
history = ["1","2","3"]

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
        print(str(i+1)+".", split_response, "\n")
        return split_response[0].replace("\n", "")
        
    



    for i in range(5):
        filtered[i] = filtering(str(database_response[i]))
    

    messages = [{"role": "system", "content": "You are an assistent designed to answer questions about Proctor Academy."}]
    
    messages.append({"role": "user", "content": str(filtered)})
    messages.append({"role": "user", "content": "Here is the chat history: " + str(history) + " Refer to this infromation is the user asks follow up questions."})

    chat = oclient.chat.completions.create(
        model="gpt-3.5-turbo", messages=messages
    )
      
    reply = chat.choices[0].message.content
    print(f"ProctorPal: {reply}")
    messages.append({"role": "assistant", "content": reply})

    print(messages)

    for i in range(2):
        
        history[0] = ("User input", i+1, "question[s] ago:", query , "Your response", i+1, "question[s] ago:", reply )

        if i < 2:
            history[i+1] = history[i]
        else:
            break
