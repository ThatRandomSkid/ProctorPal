import os
from qdrant_client import QdrantClient
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
import streamlit as st
import time
from dotenv import load_dotenv
import json

# Editable states
response_num = 7
gpt_tokens = 512
gpt_version = 3.5

# Import hidden data from .env
load_dotenv()
YOUR_API_KEY = os.getenv("OPENAI_API_KEY")
linden_key = os.getenv("linden_key")
burke_key = os.getenv("burke_key")
max_key = os.getenv("max_key")
ember_key = os.getenv("ember_key")
guest_key = os.getenv("guest_key")
linden_admin_key = os.getenv("linden_admin_key")
guest_admin_key = os.getenv("guest_admin_key")

# Initialize clients
OpenAIEmbeddings.model = "text-embedding-3-large"
oclient = OpenAI(api_key=YOUR_API_KEY)
qclient = QdrantClient("localhost", port=6333)
embeddings_model = oclient.embeddings.create

# Initilize lists/variables
filtered = []
admin = False
user = ''
if "adequacy" not in st.session_state:
    st.session_state.adequacy = None
selected_chat = 1


# Webpage design
#primaryColor="#F63366"
#backgroundColor="#FFFFFF"
#secondaryBackgroundColor="#F0F2F6"
#textColor="#262730"
#font="sans serif"

st.title("ProctorPal (beta)")
one, two, three, four, five, six, seven, eight, nine, ten, eleven, twelve = st.columns(12)
sidebar_one, sidebar_two, sidebar_three, sidebar_four, sidebar_five = st.sidebar.columns(5)
history_tab, beta_tab, sign_up_tab, login_tab, about_tab = st.sidebar.tabs(["Chat History","Beta","Sign Up", "Login", "About"])

# Account create
new_username = sign_up_tab.text_input("Username:")
new_password = sign_up_tab.text_input("Password:", type="password")

if sign_up_tab.button("Create account"):
    open("Accounts.json", 'w').write(json.dumps(({new_username: {'Username': new_username, 'Password': new_password, 'Number of chats': 1, 'Chat history' : {'1':{"user_history": [],"assistant_history": []}}}}), indent=4))

# Login
username = login_tab.text_input("Username: ")
password = login_tab.text_input("Password: ", type="password")

if password != "":
    data = json.load(open("Accounts.json", 'r'))
    if username in data and password == data[username]["Password"]:
        st.write(f"Welcome, {username}.")
        user = username
    elif username not in data:
        st.write(f"No username {username} in system.")
    elif password != data[username]["Password"]:
        st.write("Password is incorrect.")
    else:
        st.write("Username or password are incorrect.")

# Provides link to GitHub in the sidebar
about_tab.write("Developed by Linden Morgan")
about_tab.write("If you're interested in the code for this project, you can check it out here: https://github.com/ThatRandomSkid/ProctorPal")

# Gets beta key form input
beta_key = beta_tab.text_input("Your super secret beta tester key:", type="password")

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
    query = st.chat_input("Please enter beta tester key in the field to the left.")
    query = None
elif auth_state == False:
    query = st.chat_input("Beta tester key is incorrect. Please try again.")
    query = None

# Holds program until user enters text
while query ==  None:
    time.sleep(0.1)

# Gets chat history from Accounts file
data = json.load(open("Accounts.json", 'r'))
chats = data[username]["Number of chats"]

# Button that creates new chats
if history_tab.button("New Chat"):
    chats = chats + 1
    data[username]['Number of chats'] = chats 
    json.dumps(data[username]['Number of chats'])
    data[username]['Chat history'][chats] = {"user_history": [], "assistant_history": []}
    json.dumps(data[username]['Chat history'][chats], indent = 4)

# Creates session states for historic chats
for i in range(1, chats+1):
    if f"user_history{i}" not in st.session_state:
        st.session_state[f"user_history{i}"] = data[username].get(i, {}).get("user_history", [])
    if f"assistant_history{i}" not in st.session_state:
        st.session_state[f"assistant_history{i}"] = data[username].get(i, {}).get("assistant_history", [])

# Displays chat history
for i in range(chats):
    if history_tab.button(f"Chat {chats}"): # Replace with gpt-3.5 generated chat names
        selected_chat = i + 1

# Logs user query in history
st.session_state[f"user_history{selected_chat}"].append(query)

# Prints chat history
st.write(st.session_state[f"user_history{selected_chat}"])
st.write(st.session_state[f"assistant_history{selected_chat}"])

for i in range(len(st.session_state[f"user_history{selected_chat}"])):
    with st.chat_message("user"):
        st.write(st.session_state[f"user_history{selected_chat}"][i])
    if i < len(st.session_state[f"assistant_history{selected_chat}"]) and len(st.session_state[f"assistant_history{selected_chat}"]) != 0:
            with st.chat_message("assistant"):
                st.write(st.session_state[f"assistant_history{selected_chat}"][i-1])
            st.write(len((st.session_state[f"assistant_history{selected_chat}"])))
            st.write("testing")


# Embeds database querys 
embedded_query = embeddings_model(input = [query], model="text-embedding-3-large").data[0].embedding

# Get database output
database_response = qclient.search( 
    collection_name="test_collection11", query_vector=embedded_query, limit=response_num
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
messages = [{"role": "system", "content": "You are an assistant designed to answer questions about Proctor Academy. Here is the user question: " + str(query) + "Do not reference the fact that this data was given to you to the user, pretend like you know it."}]
messages.append({"role": "system", "content": "Here is some information: " + str(filtered) + "Include only the parts that are relevant to the user question."})

# Prints API input for easier debugging
if admin == True:
    st.write(str(filtered))

# Sets ChatGPT model
if gpt_version == 3.5:
    gpt_version = "gpt-3.5-turbo-0125"
elif gpt_version == 4:
    gpt_version = "gpt-4-turbo-preview"

# Gets ChatGPT api response
chat = oclient.chat.completions.create(
    model=gpt_version, messages=messages, max_tokens=gpt_tokens
)
reply = chat.choices[0].message.content

# Logs ChatGPT response in history
st.session_state[f"assistant_history{selected_chat}"].append(reply)

# Prints ChatGPT response
with st.chat_message("assistant"):
    st.write(st.session_state[f"assistant_history{selected_chat}"][-1])
    st.write(len((st.session_state[f"assistant_history{selected_chat}"])))


# Updates logs
if admin == False and user != "Linden (user)":
    f1 = open("Logs.txt", "a")
    f1.write("\n\n" + user + ": " + query + "\n" + "ProctorPal: " + reply)
    f1.close()

# Buttons allowing user rate responses
if st.button("Response was inadequate"): 
    f2 = open("Unanswered_Questions.txt", "a")
    f2.write("\n\n" + user + ": " + query + "\n" + "ProctorPal: " + reply)
    f2.close()