import os
import openai
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
import json
import streamlit as st
import time
from dotenv import load_dotenv

# Editable states
response_num = 7
gpt_tokens = 512
gpt_version = 4

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
filtered = []
admin = False
user = ''
if "user_history" not in st.session_state:
    st.session_state.user_history = []
if "assistant_history" not in st.session_state:
    st.session_state.assistant_history = []
if "adequacy" not in st.session_state:
    st.session_state.adequacy = None

# Webpage design
#primaryColor="#F63366"
#backgroundColor="#FFFFFF"
#secondaryBackgroundColor="#F0F2F6"
#textColor="#262730"
#font="sans serif"

st.title("ProctorPal (beta)")
one, two, three, four, five, six, seven, eight, nine, ten, eleven, twelve = st.columns(12)
sidebar_one, sidebar_two, sidebar_three, sidebar_four, sidebar_five = st.sidebar.columns(5)

# Gets beta key form input
beta_key = st.sidebar.text_input("Your super secret beta tester key:")

# Provides link to GitHub in the sidebar
for i in range(31):
    st.sidebar.write('')
st.sidebar.write("Developed by Linden Morgan")
st.sidebar.write("If you're interested in the code for this project, you can check it out here: https://github.com/ThatRandomSkid/ProctorPal")

# Determine user
if beta_key == linden_key:
    user = "Linden (user)"
if beta_key == burke_key:
    user = "Burke"
if beta_key == max_key:
    user = "Max"
if beta_key == ember_key:
    user = "Ember"
if beta_key == guest_key:
    user = "Guest"
if beta_key == linden_admin_key:
    user = "Linden (admin)"
    admin = True
if beta_key == guest_admin_key:
    user = "Guest (admin)"
    admin = True

# User authenication
if beta_key == '':
    auth_state = None
    query = None
elif beta_key == linden_key or beta_key == burke_key or beta_key ==  max_key or beta_key == ember_key or beta_key == guest_key:
    auth_state = True
    pass
elif beta_key == linden_admin_key or beta_key == guest_admin_key:
    auth_state = True
    pass
else:
    auth_state = False
    query = None
    
# Gets user input from site 
if auth_state == True :
    query = st.chat_input(user + ":")
elif auth_state == None:
    query = st.chat_input("Please enter beta tester key in the feild to the left.")
    query = None
elif auth_state == False:
    query = st.chat_input("Beta tester key is incorrect. Please try again.")
    query = None

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
    collection_name="test_collection4", query_vector=embedded_query, limit=response_num
)

# Filter database response (replace with valid json implimentation eventually)
def filtering(response):
    split_response = str(response).split(":")
    split_response = str(split_response[1]).split("}")
    print(str(i+1)+".", split_response, "\n")
    return split_response[0].replace("\n", "")

for i in range(response_num):
    filtered.append(filtering(str(database_response[i])))

# Gives ChatGPT api input
messages = [{"role": "system", "content": "You are an assistent designed to answer questions about Proctor Academy. Here is the user question: " + str(query) + "Do not referance the fact that this data was given to you to the user, pretend like you know it."}]
messages.append({"role": "system", "content": "Here is some information: " + str(filtered) + "Include only the parts that are relavant to the user question."})

# Prints API input for easier debugging
if admin == True:
    st.write(str(filtered))

# Sets ChatGPT model
if gpt_version == 3.5:
    gpt_version = "gpt-3.5-turbo"
elif gpt_version == 4:
    gpt_version = "gpt-4"

# Gets ChatGPT api response
chat = oclient.chat.completions.create(
    model=gpt_version, messages=messages, max_tokens=gpt_tokens
)
reply = chat.choices[0].message.content

# Updates logs
if admin == False and user != "Linden (user)":
    f1 = open("Logs.txt", "a")
    f1.write("\n\n" + user + ": " + query + "\n" + "ProctorPal: " + reply)
    f1.close()

# Logs ChatGPT response in history
st.session_state.assistant_history.append(reply)

# Prints ChatGPT response
with st.chat_message("assistant"):
    st.write(st.session_state.assistant_history[-1])

# Buttons allowing user rate responses
if st.button("Response was inadequate"): 
    st.session_state.adequacy = False

# Checks for insufficient data
if st.session_state.adequacy is False:
    f2 = open("Unanswered_Questions.txt", "a")
    f2.write("\n\n"+ st.session_state.assistant_history[-1])
    f2.close()
    st.session_state.adequacy = None