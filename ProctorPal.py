import os
import openai
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
import json
import streamlit as st
import time
from dotenv import load_dotenv


# Import hidden data from .env
load_dotenv()
YOUR_API_KEY = os.getenv("YOUR_API_KEY")
linden_key = os.getenv("linden_key")
burke_key = os.getenv("burke_key")
max_key = os.getenv("max_key")
ember_key = os.getenv("ember_key")
guest_key = os.getenv("guest_key")
linden_admin_key = os.getenv("linden_admin_key")
guest_admin_key = os.getenv("guest_admin_key")

# Initialize clients
OpenAIEmbeddings.model = "text-embedding-3-large"
embeddings_model = OpenAIEmbeddings(openai_api_key=YOUR_API_KEY)
oclient = OpenAI(api_key=YOUR_API_KEY)
qclient = QdrantClient("localhost", port=6333)

# Initilize lists/variables
filtered = ["1","2","3","4","5"]
admin = False
user = ''
if "user_history" not in st.session_state:
    st.session_state.user_history = []
if "assistant_history" not in st.session_state:
    st.session_state.assistant_history = []


# Webpage design
#primaryColor="#F63366"
#backgroundColor="#FFFFFF"
#secondaryBackgroundColor="#F0F2F6"
#textColor="#262730"
#font="sans serif"

"""# ProctorPal (beta)"""
one, two, three, four, five = st.columns(5)

# Gets beta key form input
beta_key = st.sidebar.text_input("Your super secret beta tester key:")
for i in range(37):
    st.sidebar.write('')
st.sidebar.write("If you're intresed in the code for this project, you can check it out here: https://github.com/ThatRandomSkid/ProctorPal")

# Determine user
if beta_key == linden_key:
    user = "Linden (user)"
if beta_key == burke_key:
    user = "Burke"
if beta_key == max_key:
    user = "Max"
if beta_key == ember_key:
    user = "Ember"
if beta_key == ember_key:
    user = "Guest"
if beta_key == linden_admin_key:
    user = "Linden (admin)"
    admin = True
if beta_key == guest_admin_key:
    user = "Guest (admin)"
    admin = True

# Gets user input from site 
if user == '':
    query = st.chat_input('')
if user != '':
    query = st.chat_input(user + ":")

# Locks out non-authenticated users
if beta_key == '':
    st.write("Please enter beta tester key.")
    query = None
elif beta_key == linden_key or beta_key == burke_key or beta_key ==  max_key or beta_key == ember_key or beta_key == guest_key:
    pass
elif beta_key == linden_admin_key or beta_key == guest_admin_key:
    pass
else:
    query = None
    st.write("Beta tester key is incorrect. Please try again.")

# Holds program until user enters text
while query ==  None:
    time.sleep(0.1)

# Logs user query in history
st.session_state.user_history.append(query)

# Prints chat history
for i in range(len(st.session_state.user_history)):
    with st.chat_message("user"):
        st.write(st.session_state.user_history[i])
    if len(st.session_state.assistant_history) != 0 and i < len(st.session_state.assistant_history):
        with st.chat_message("assistant"):
            st.write(st.session_state.assistant_history[i-1])

# Querys database
embedded_query = embeddings_model.embed_query(str(query))

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
messages = [{"role": "system", "content": "You are an assistent designed to answer questions about Proctor Academy. Here is the user question: " + str(query) + "do not referance the fact that this data was given to you to the user, pretend like you know it."}]
messages.append({"role": "system", "content": "Here is some information: " + str(filtered) + "Include only the parts that are relavant to the user question."})

# Prints API input for easier debugging
if admin == True:
    st.write(messages)

# Gets ChatGPT api response
chat = oclient.chat.completions.create(
    model="gpt-3.5-turbo", messages=messages, max_tokens=420
)
reply = chat.choices[0].message.content

# Updates logs
if admin == False:
    f1 = open("Logs.txt", "a")
    f1.write("\n" + user + ": " + query + "\n" + "ProctorPal: " + reply)
    f1.close()

# Checks for insufficient data
if "Insufficient data." in reply:
    reply.replace("Insufficient data.", '')
    f2 = open("Unanswered_Questions.txt", "a")
    f2.write("\n" + query)
    f2.close()

# Logs ChatGPT response in history
st.session_state.assistant_history.append(reply)

# Prints ChatGPT response
with st.chat_message("assistant"):
    st.write(st.session_state.assistant_history[-1])