import os
from qdrant_client import QdrantClient
from openai import OpenAI
import streamlit as st
import time
from dotenv import load_dotenv
import json


# Editable states
gpt_version = 3.5
gpt_tokens = 512
response_num = 7
database_ip = "localhost"
database_name = "db3"


# Import hidden data from .env
load_dotenv()
YOUR_API_KEY = os.environ["OPENAI_API_KEY"]
admin_key = os.environ["admin_key"]

# Initialize clients
oclient = OpenAI(api_key=YOUR_API_KEY)
qclient = QdrantClient(database_ip, port=6333)
embeddings_model = oclient.embeddings.create

# Initilize lists/variables
filtered = []
admin = False
query = ''
if "user" not in st.session_state:
    st.session_state["user"] = ''
chats = 1
new_password = False
if "create_account" not in st.session_state:
    st.session_state["create_account"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ''
if st.session_state["username"] != '':
    username = st.session_state["username"]
if "password" not in st.session_state:
    st.session_state["password"] = ''
new_password2 = False
selected_chat = 1
accounts_read = open("Accounts.json", 'r')
data = json.load(accounts_read)



# Webage deisgn/setup
st.set_page_config(page_title='ProctorPal', page_icon = "./Profile_Pictures/ProctorPal.png")
st.title("ProctorPal (beta)")
one, two, three, four, five = st.sidebar.columns(5)

with st.chat_message("assistant", avatar = "./Profile_Pictures/ProctorPal.png"): 
    st.write("Hello! I am ProctorPal, a helpful AI assistant designed to assist with all manner of Proctor related questions. For the best experience, please login or create an account in the field to the left.")

# Login
if st.session_state["user"] == '' and st.session_state["create_account"] == False:
    st.sidebar.subheader("Login")

    # Get username/password input
    st.session_state["username"] = st.sidebar.text_input("Username: ")
    st.session_state["password"] = st.sidebar.text_input("Password: ", type="password")

    # Sets username/password for code
    username = st.session_state["username"]
    password = st.session_state["password"]

    if password != "":
        if username in data and password == data[username]["Password"]:
            st.session_state["user"] = username
            if username == "test":  # Makes testing account correspond to Tester as a user 
                st.session_state["user"] = "Tester"
            st.session_state["create_account"] = None
            st.rerun()
            
        elif username not in data:
            st.sidebar.write(f'No username "{username}" in system.')

        elif password != data[username]["Password"]:
            st.sidebar.write("Password is incorrect.")

        else:
            st.sidebar.write("Username or password are incorrect.")

# Button allowing user to create an account if they don't already have one
if st.session_state["create_account"] == False:
    st.sidebar.write("Don't have an account? Create one here:")
    if st.sidebar.button("Create account"):
        st.session_state["create_account"] = True
        if st.session_state["user"] == '':
            st.rerun()

# Account create
if st.session_state["create_account"] == True and st.session_state["user"] == '':
    st.sidebar.subheader("Create Account")
    new_username = st.sidebar.text_input("Username:")
    new_password = st.sidebar.text_input("Password:", type="password")
    new_password2 = st.sidebar.text_input("Re-enter password:", type="password")

    if new_username in data:
        st.sidebar.write("Username already taken. Please try again.") 

    elif new_password != new_password2 and new_password != "" and new_password2 != "":
        st.sidebar.write("Passwords do not match.")

    elif new_password and new_password2 and new_username != "": 
        if st.sidebar.button("Create account"):
            data.update({new_username: {'Username': new_username, 'Password': new_password, 'Number of chats': 1, 'Chat history' : {'1':{"user_history": [],"assistant_history": []}}}})
            open("Accounts.json", 'w').write(json.dumps(data, indent=4))

            # Login
            st.session_state["username"] = new_username
            st.session_state["user"] = new_username
            st.session_state["create_account"] = None
            st.rerun()

# Login button to get back from account creation
with st.container():
    if st.session_state["create_account"] == True:
        st.sidebar.write("Have an account? Login here:")
        if st.sidebar.button("Login"):
            st.session_state["create_account"] = False
            if st.session_state["user"] == '':
                st.rerun()

# Logged in display
if st.session_state["user"] != '':
    st.sidebar.subheader(f"Currently logged in as {username}.")

    # Sets a welecome message
    if st.session_state["user"] != "Guest":
        welcome_message = f"Welcome, {username}!"

    # Account settings
    if st.session_state["user"] != '':
        with st.sidebar.expander("Account Settings"):
            if st.text_input("Beta tester keys go here:") == admin_key:
                admin = True

    # Log out button
    if st.sidebar.button("Log out"):
        st.session_state["user"] = ''
        st.session_state["username"] = ''
        st.session_state["password"] = ''
        st.session_state["create_account"] = False
        st.rerun()
    
    # Creates session states for historic chats
    if username != "Guest" and st.session_state["user"] != "":
        for i in range(1, chats+1):
            if f"user_history{i}" not in st.session_state:
                st.session_state[f"user_history{i}"] = data[username]['Chat history'][str(i)]['user_history']
            if f"assistant_history{i}" not in st.session_state:
                st.session_state[f"assistant_history{i}"] = data[username]['Chat history'][str(i)]['assistant_history']
        
    # Prints chat
    for i in range(len(st.session_state[f"user_history{selected_chat}"])): 
        with st.chat_message("user"):
            st.write(st.session_state[f"user_history{selected_chat}"][i])
        if i < len(st.session_state[f"assistant_history{selected_chat}"]):
                with st.chat_message("assistant", avatar = "./Profile_Pictures/ProctorPal.png"):
                    st.write(st.session_state[f"assistant_history{selected_chat}"][i])

# Provides link to GitHub in the sidebar
with st.container():
    for i in range(20):
        st.sidebar.write('')
    st.sidebar.write("Developed by Linden Morgan")
    st.sidebar.write("If you're interested in the code for ProctorPal, you can check it out here: https://github.com/ThatRandomSkid/ProctorPal")

# Decides what text to display in chat input feild
if admin == True:
    display = st.session_state["user"] + " (admin):"
elif st.session_state["user"] != '':
    display = st.session_state["user"] + ":"
else:
    display = "Ask a question here:"

# Gets user input from site 
query = st.chat_input(display)

# Sets query for guest
if st.session_state["username"] == "Guest":
    if not st.session_state["user_history1"]:
        query = st.session_state["guest_query_1"]



# Holds program until user enters text
while query ==  None:
    time.sleep(0.1)

# Sets account to Guest if input is entered without logging in
if st.session_state["user"] == '':
    st.session_state["username"] = "Guest"
    st.session_state["user"] = "Guest"
    # Creates session states for historic chats
    if "user_history1" not in st.session_state:
        st.session_state["user_history1"] = []
    if "assistant_history1" not in st.session_state:
        st.session_state["assistant_history1"] = []
    if "guest_query_1" not in st.session_state:
        st.session_state["guest_query_1"] = query
    st.rerun()

# Logs user query in history
st.session_state[f"user_history{selected_chat}"].append(query)

# Writes question user just entered
with st.chat_message("user"):
    st.write(query)

# Prints degbug info if admin flair is active
if admin == True:
    st.write(st.session_state[f"user_history{selected_chat}"])
    st.write(st.session_state[f"assistant_history{selected_chat}"])

# Set chat history of ChatGPT input
if len(st.session_state[f"user_history{selected_chat}"]) > 1: 
    chat_history = st.session_state[f"user_history{selected_chat}"][-1] + st.session_state[f"assistant_history{selected_chat}"][-1]
else:
    chat_history = st.session_state[f"user_history{selected_chat}"] + st.session_state[f"assistant_history{selected_chat}"]

# Converts database query to vector 
embedded_query = embeddings_model(input = [query], model="text-embedding-3-large").data[0].embedding

# Get database output
database_response = qclient.search( 
    collection_name=database_name, query_vector=embedded_query, limit=response_num
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
messages.append({"role": "system", "content": "Here is some information: " + str(filtered) + "Include only the parts that are relevant to the user question. Do NOT answer questions that aren't about Proctor. Here is some background infromation:" + str(chat_history)})

# Prints API input for easier debugging
if admin == True:
    st.write(str(messages))

# Sets ChatGPT model
if gpt_version == 3.5:
    gpt_version = "gpt-3.5-turbo-0125"
elif gpt_version == 4:
    gpt_version = "gpt-4-turbo-preview"

# Gets/Prints ChatGPT api response
with st.chat_message("assistant", avatar = "./Profile_Pictures/ProctorPal.png"): 
    with st.spinner("Thinking..."):
        chat = oclient.chat.completions.create(
        model = gpt_version, messages=messages, max_tokens=gpt_tokens
        )
        reply = chat.choices[0].message.content
        st.write(reply) # Prints ChatGPT response

# Logs ChatGPT response in history
st.session_state[f"assistant_history{selected_chat}"].append(reply)

# Logs chat history in the accounts file
if username != "Guest" and  username != "test":
    user_history = st.session_state[f"user_history{selected_chat}"][-1]
    assistant_history = st.session_state[f"assistant_history{selected_chat}"][-1]

    #data[username]['Chat history'][str(selected_chat)]['user_history'].append(user_history)
    #data[username]['Chat history'][str(selected_chat)]['assistant_history'].append(assistant_history)

    with open("Accounts.json", 'w') as accounts_file:
        json.dump(data, accounts_file, indent=4)

# Logs chat in history section of account file
if admin == True:
    st.write(data[username]['Chat history'][str(selected_chat)])

# Updates logs
if username != "test" and admin == False:
    with open("Logs.txt", "a") as f1:
        f1.write("\n\n" + username + ": " + query + "\n" + "ProctorPal: " + reply)