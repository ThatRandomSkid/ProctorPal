import os
from qdrant_client import QdrantClient
from openai import OpenAI
import streamlit as st
import time
from dotenv import load_dotenv
import json
import extra_streamlit_components as stx


# Editable settings
gpt_version = 4
gpt_tokens = 512
response_num = 7

# Gets settings from settings.json file
settings_path = os.path.expanduser("~/ProctorPal/settings.json")
with open(settings_path, 'r') as f:
    d = json.load(f)
    database_ip = d.get("database_ip")
    database_name = d.get("database_name")

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
if "cookies_active" not in st.session_state:
    st.session_state["cookies_active"] = ''
if "use_cookies" not in st.session_state:
    st.session_state["use_cookies"] = ''
if "prevent_auto_sign_in" not in st.session_state:
    st.session_state["prevent_auto_sign_in"] = False
if "clear" not in st.session_state:
    st.session_state["clear"] = 0
new_password2 = False
selected_chat = 1
accounts_read = open("Accounts.json", 'r')
data = json.load(accounts_read)
about_hight = 12


# Webage deisgn/setup
st.set_page_config(page_title='ProctorPal', page_icon = "./Profile_Pictures/ProctorPal.png")
st.title("ProctorPal (beta)")
one, two, three, four, five = st.sidebar.columns(5)

with st.chat_message("assistant", avatar = "./Profile_Pictures/ProctorPal.png"): 
    st.write("""Hello! I am ProctorPal, a helpful AI assistant designed to assist with all manner of Proctor related questions. 
             For the best experience, please login or create an account in the field to the left. 
             Please be aware that while I can be a helpful tool, I am capable of making mistakes and you should never make impotant decisions 
             based on my guidence.""")

# Cookie setup
def get_manager():
    return stx.CookieManager()
cookie_manager = get_manager()

cookie_user = cookie_manager.get(cookie="cookie_user") # Gets username cookie
cookie_pass = cookie_manager.get(cookie="cookie_pass") # Gets password cookie

print("Cookies:", cookie_user, cookie_pass)
if cookie_user == '':
    cookie_user = None
if cookie_pass == '':
    cookie_pass = None

# Saves authenication cookies if none exist
if st.session_state["cookies_active"] == True and st.session_state["use_cookies"] == True:
    if cookie_user != st.session_state["username"] or cookie_pass != st.session_state["password"]:
        if cookie_user != None and cookie_pass != None:
            cookie_manager.delete("cookie_user", key = "a")
            cookie_manager.delete("cookie_pass", key = "b")
            print("cookies deleted0")

        cookie_manager.set("cookie_user", st.session_state["username"],  key = "c")
        cookie_manager.set("cookie_pass", st.session_state["password"], key = "d")
        print("cookies set:", cookie_manager.get(cookie="cookie_user"), cookie_manager.get(cookie="cookie_pass"))

# Login
if st.session_state["user"] == '' and st.session_state["create_account"] == False:

    # Get username/password from input if there is no authentication cookie
    if cookie_user == None or cookie_pass == None or st.session_state["prevent_auto_sign_in"] == True:
        st.sidebar.subheader("Login")
        st.session_state["username"] = st.sidebar.text_input("Username: ", key = st.session_state["clear"])
        st.session_state["password"] = st.sidebar.text_input("Password: ", type="password", key = st.session_state["clear"]+1)
        st.session_state["use_cookies"] = st.sidebar.checkbox("Keep me signed in (uses cookies)", value=True, key = st.session_state["clear"]+2)

        data[username]["Uses cookies"] = st.session_state["use_cookies"] # Updates uses cookies flag key Accounts.json
        json.dump(data, accounts_read, indent=4)

        # Deletes cookie if use_cookies is set to false
        if st.session_state["use_cookies"] == False and cookie_pass != None and cookie_user != None: 
            cookie_manager.delete("cookie_user")
            cookie_manager.delete("cookie_pass")
            print("cookie deleted")

    # If there is an authenication cookie sets username/password from authentication cookie
    elif cookie_user != None and cookie_pass != None and st.session_state["prevent_auto_sign_in"] == False:
        st.session_state["username"] = cookie_user
        st.session_state["password"] = cookie_pass
    
    # Sets username/password for code
    username = st.session_state["username"]
    password = st.session_state["password"]

    # Logs user in
    if password != "" and username != "":
        if (username in data and password == data[username]["Password"]):
            st.session_state["user"] = username
            if username == "test":  # Makes testing account correspond to Tester as a user
                st.session_state["user"] = "Tester"
            st.session_state["create_account"] = None

            # Enables create cookie script at the begining of code
            st.session_state["cookies_active"] = True
                    
            st.rerun()
            
        elif username not in data:
            st.sidebar.write(f'No username "{username}" in system.')

        elif password != data[username]["Password"]:
            st.sidebar.write("Password is incorrect.")

        else:
            st.sidebar.write("Username or password are incorrect.")

# Button allowing user to create an account if they don't already have one
if st.session_state["create_account"] == False:
    for i in range(2):
        st.sidebar.write("")
    st.sidebar.subheader("Sign Up")
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
    st.session_state["use_cookies"] = st.sidebar.checkbox("Keep me signed in (uses cookies)", value=True)

    if new_username in data:
        st.sidebar.write("Username already taken. Please try again.") 

    elif new_password != new_password2 and new_password != "" and new_password2 != "":
        st.sidebar.write("Passwords do not match.")

    elif new_password != "" and new_password2 != "" and new_username != "":  
        if st.sidebar.button("Create account"):
            data.update({new_username: {'Username': new_username, 'Password': new_password, 'Number of chats': 1, 'Uses cookies' : st.session_state["use_cookies"], 'Chat history' : {'1':{"user_history": [],"assistant_history": []}}}})
            open("Accounts.json", 'w').write(json.dumps(data, indent=4))

            # Login
            st.session_state["username"] = new_username
            st.session_state["user"] = new_username
            st.session_state["create_account"] = None
            st.rerun()

# Login button to get back from account creation
if st.session_state["create_account"] == True:
    for i in range(2):
        st.sidebar.write("")
    st.sidebar.subheader("Login")
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
        st.session_state["prevent_auto_sign_in"] = True
        st.session_state["cookies_active"] = False
        st.session_state["clear"] += 1
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
for i in range(about_hight):
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
    return split_response[0].replace("\n", "")

for i in range(response_num):
    filtered.append(filtering(str(database_response[i])))

# Gives ChatGPT api input
messages = [{"role": "system", "content": f"""You are an assistant designed to answer questions about Proctor Academy. 
             It is ok if you cannot answer a question with the data given, but DO NOT make up answers when the information was not given to you in the context.
             Here is the user question: {str(query)} 
             Here is some potentially relevant information, but not all of it will be usefull. Generally, the infromation that comes earlier will be more relevant: {str(filtered)} 
             Include only the parts that are relevant to the user question. DO NOT answer questions that aren't about Proctor."""}]

# Prints API input for easier debugging
if admin == True:
    st.write(str(messages))

# Sets ChatGPT version
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

    data[username]['Chat history'][str(selected_chat)]['user_history'].append(user_history)
    data[username]['Chat history'][str(selected_chat)]['assistant_history'].append(assistant_history)

    with open("Accounts.json", 'w') as accounts_file:
        json.dump(data, accounts_file, indent=4)

# Logs chat in history section of account file
if admin == True:
    st.write(data[username]['Chat history'][str(selected_chat)])

# Updates logs
if username != "test" and admin == False:
    with open("Logs.txt", "a") as f1:
        f1.write("\n\n" + username + ": " + query + "\n" + "ProctorPal: " + reply)