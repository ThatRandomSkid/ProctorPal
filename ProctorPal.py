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
admin_key = os.getenv("admin_key")

# Initialize clients
OpenAIEmbeddings.model = "text-embedding-3-large"
oclient = OpenAI(api_key=YOUR_API_KEY)
qclient = QdrantClient("localhost", port=6333)
embeddings_model = oclient.embeddings.create

# Initilize lists/variables
filtered = []
admin = False
user = ''
new_password = False
new_password2 = False
if "adequacy" not in st.session_state:
    st.session_state.adequacy = None
selected_chat = 1
accounts_read = open("Accounts.json", 'r')
data = json.load(accounts_read)



st.title("ProctorPal (beta)")
one, two, three, four, five, six, seven, eight, nine, ten, eleven, twelve = st.columns(12)
sidebar_one, sidebar_two, sidebar_three, sidebar_four, sidebar_five = st.sidebar.columns(5)
history_tab, sign_up_tab, login_tab, about_tab = st.sidebar.tabs(["Chat History","Sign Up", "Login", "About"])

# Account create
new_username = sign_up_tab.text_input("Username:")
new_password = sign_up_tab.text_input("Password:", type="password")
new_password2 = sign_up_tab.text_input("Re-enter password:", type="password")

if new_username in data:
    sign_up_tab.write("Username already taken. Please try again.") 

elif new_password != new_password2:
    sign_up_tab.write("Passwords do not match.")

elif sign_up_tab.button("Create account"):
    data.update({new_username: {'Username': new_username, 'Password': new_password, 'Number of chats': 1, 'Chat history' : {'1':{"user_history": [],"assistant_history": []}}}})
    open("Accounts.json", 'w').write(json.dumps(data, indent=4))

# Login
username = login_tab.text_input("Username: ")
password = login_tab.text_input("Password: ", type="password")

if password != "":
    if username in data and password == data[username]["Password"]:
        login_tab.write(f"Welcome, {username}.")
        user = username

    elif username not in data:
        login_tab.write(f"No username {username} in system.")

    elif password != data[username]["Password"]:
        login_tab.write("Password is incorrect.")

    else:
        login_tab.write("Username or password are incorrect.")

# Account settings
if user != '':
    with login_tab.expander("Account Settings"):
        if st.text_input("Beta tester keys go here:") == admin_key:
            admin = True

# Provides link to GitHub in the sidebar
about_tab.write("Developed by Linden Morgan")
about_tab.write("If you're interested in the code for this project, you can check it out here: https://github.com/ThatRandomSkid/ProctorPal")

# Decides what text to display in chat input feild
if user == "test":
    display = "Tester:"
    if admin == True:
        display == "Tester (admin)"
if admin == True:
    display = f"{user} (admin):"
elif user != '':
    display = user
else:
    display = "Ask a question here:"

# Gets user input from site 
query = st.chat_input(display)

# Holds program until user enters text
while query ==  None:
    time.sleep(0.1)

# Provides guest account if not logged in 
if user == '':
    username = "Guest"

# Gets number of chats from accounts file
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
        st.session_state[f"user_history{i}"] = data[username]['Chat history'][str(i)]['user_history']
    if f"assistant_history{i}" not in st.session_state:
        st.session_state[f"assistant_history{i}"] = data[username]['Chat history'][str(i)]['assistant_history']

# Displays chat history
for i in range(chats):
    if history_tab.button(f"Chat {chats}"): # Replace with gpt-3.5 generated chat names
        selected_chat = i + 1

# Logs user query in history
st.session_state[f"user_history{selected_chat}"].append(query)

# Prints chat history
if admin == True:
    st.write(st.session_state[f"user_history{selected_chat}"])
    st.write(st.session_state[f"assistant_history{selected_chat}"])

for i in range(len(st.session_state[f"user_history{selected_chat}"])):
    with st.chat_message("user"):
        st.write(st.session_state[f"user_history{selected_chat}"][i])
    if i < len(st.session_state[f"assistant_history{selected_chat}"]):
            with st.chat_message("assistant"):
                st.write(st.session_state[f"assistant_history{selected_chat}"][i])



# Converts database query to vector 
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
with st.spinner("Thinking..."):
    chat = oclient.chat.completions.create(
        model=gpt_version, messages=messages, max_tokens=gpt_tokens
    )
    reply = chat.choices[0].message.content

# Prints ChatGPT response
with st.chat_message("assistant"): 
    st.write(reply)

# Logs ChatGPT response in history
st.session_state[f"assistant_history{selected_chat}"].append(reply)

# Logs chat in history section of account file
if admin == True:
    st.write(data[username]['Chat history'][str(selected_chat)])

data[username]['Chat history'][str(selected_chat)]['user_history'] = st.session_state[f"user_history{selected_chat}"] 
data[username]['Chat history'][str(selected_chat)]['assistant_history'] = st.session_state[f"assistant_history{selected_chat}"]
json.dumps(data[username]['Chat history'][str(selected_chat)]['user_history'], indent = 4)
json.dumps(data[username]['Chat history'][str(selected_chat)]['assistant_history'], indent = 4)

# Updates logs
if admin == False and user != "Linden Morgan" or "test":
    f1 = open("Logs.txt", "a")
    f1.write("\n\n" + user + ": " + query + "\n" + "ProctorPal: " + reply)
    f1.close()

# Buttons allowing user rate responses
if st.button("Response was inadequate"): 
    f2 = open("Unanswered_Questions.txt", "a")
    f2.write("\n\n" + user + ": " + query + "\n" + "ProctorPal: " + reply)
    f2.close()