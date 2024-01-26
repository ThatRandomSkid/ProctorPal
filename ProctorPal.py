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
embeddings_model = OpenAIEmbeddings(openai_api_key=YOUR_API_KEY)
oclient = OpenAI(api_key=YOUR_API_KEY)
qclient = QdrantClient("localhost", port=6333)

# Initilize lists/variables
filtered = ["1","2","3","4","5"]
admin = False
user = ''


# Webpage design
"""# ProctorPal (beta)"""
one, two, three, four, five = st.columns(5)

# Gets beta key form input
beta_key = st.sidebar.text_input("Your super secret beta tester key:")
st.sidebar.write("If you're intresed in the code for this project, you can check it out here: https://github.com/ThatRandomSkid/ProctorPal")

# Determine User
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
    query = st.text_input('')
if user != '':
    query = st.text_input(user + ":")

# Locks out non-authenticated users
if beta_key == '':
    st.write("Please enter beta tester key.")
    query = ''
elif beta_key == linden_key or beta_key == burke_key or beta_key ==  max_key or beta_key == ember_key or beta_key == guest_key:
    pass
elif beta_key == linden_admin_key or beta_key == guest_admin_key:
    pass
else:
    query = ''
    st.write("Beta tester key is incorrect. Please try again.")

# Holds program until user enters text
while query == '':
    time.sleep(0.1)


# Querys database
embedded_query = embeddings_model.embed_query(query)

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
messages.append({"role": "system", "content": "Here is some information: " + str(filtered) + "Include only the parts that are relavant to the user question."})
messages.append({"role": "user", "content": "If you aren't provided *any* relevant data to answer a question, add Insufficient data. at the end of your response, but still include the normal response beforehand. Do not put it in brackets."})

if admin == True:
    st.write(messages)

# Gets ChatGPT api response
chat = oclient.chat.completions.create(
    model="gpt-3.5-turbo", messages=messages, max_tokens=512
)
reply = chat.choices[0].message.content

# Updates logs
if admin == False:
    f1 = open("Logs.txt", "a")
    f1.write(user + ": " + query + "\n" + "ProctorPal: " + reply + "\n")
    f1.close()

# Checks for insufficient data
if "Insufficient data." in reply:
    reply.replace("Insufficient data.", '')
    f2 = open("Unanswered_Questions.txt", "a")
    f2.write("\n" + query)
    f2.close()

# Returns ChatGPT response
st.write(f"ProctorPal: {reply}")