import os
from qdrant_client import QdrantClient
from openai import OpenAI
import streamlit as st
import time
from dotenv import load_dotenv
import json
import extra_streamlit_components as stx
import tiktoken

# Starts timer for code
code_time = time.time()

# Editable settings
gpt_version = 3.5
gpt_tokens = 512
gpt_temperature = 1
response_num = 7


# Gets settings from settings.json file
settings_path = os.path.expanduser("~/ProctorPal/settings.json")
with open(settings_path, 'r') as f:
    settings = json.load(f)
    database_ip = settings.get("database_ip")
    database_name = settings.get("database_name")
    site_title = settings.get("site_title")

# Import hidden data from .env
load_dotenv()
YOUR_API_KEY = os.environ["OPENAI_API_KEY"]
admin_key = os.environ["admin_key"]

# Initialize clients
oclient = OpenAI(api_key=YOUR_API_KEY)
qclient = QdrantClient(database_ip, port=6333)
embeddings_model = oclient.embeddings.create

# Initilize lists/variables/session states 
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
if "pfp_filepath" not in st.session_state:
    st.session_state["pfp_filepath"] = "null"
if "number_of_chats" not in st.session_state:
    st.session_state["number_of_chats"] = 1
if "selected_chat_name" not in st.session_state:
    st.session_state["selected_chat_name"] = ''
new_password2 = False
selected_chat = 1
accounts_read = open("accounts.json", 'r')
data = json.load(accounts_read)
about_hight = 12




# Webage deisgn/setup
st.set_page_config(page_title = site_title, page_icon = "./profile_pictures/ProctorPal.png")
st.title("ProctorPal (beta)")
one, two, three, four, five = st.sidebar.columns(5)

with st.chat_message("assistant", avatar = "./profile_pictures/ProctorPal.png"): 
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

if cookie_user == '':
    cookie_user = None
if cookie_pass == '':
    cookie_pass = None

# Saves authenication cookies if none exist
if st.session_state["cookies_active"] == True and st.session_state["use_cookies"] == True:
    if cookie_user != st.session_state["username"] or cookie_pass != st.session_state["password"]:
        if cookie_user != None and cookie_pass != None: # Deletes any exiting cookies
            cookie_manager.delete("cookie_user", key = "a")
            cookie_manager.delete("cookie_pass", key = "b")
        cookie_manager.set("cookie_user", st.session_state["username"],  key = "c")
        cookie_manager.set("cookie_pass", st.session_state["password"], key = "d")

# Login
if st.session_state["user"] == '' and st.session_state["create_account"] == False:

    # Get username/password from input if there is no authentication cookie
    if cookie_user == None or cookie_pass == None or st.session_state["prevent_auto_sign_in"] == True:
        st.sidebar.subheader("Login")
        st.session_state["username"] = st.sidebar.text_input("Username: ", key = st.session_state["clear"])
        st.session_state["password"] = st.sidebar.text_input("Password: ", type="password", key = st.session_state["clear"]+1)
        st.session_state["use_cookies"] = st.sidebar.checkbox("Keep me signed in (uses cookies)", value=True, key = st.session_state["clear"]+2)

        if st.session_state["username"] != '' and st.session_state["password"] != '':
            accounts_read = open("accounts.json", 'r')
            data = json.load(accounts_read)
            with open("accounts.json", 'w') as accounts_write:
                data[st.session_state["username"]]["uses cookies"] = st.session_state["use_cookies"] # Updates uses cookies flag accounts.json
                json.dump(data, accounts_write, indent=4)

        # Deletes cookie if use_cookies is set to false
        if st.session_state["use_cookies"] == False and cookie_pass != None and cookie_user != None: 
            cookie_manager.delete("cookie_user", key = "y")
            cookie_manager.delete("cookie_pass", key = "z")

    # If there is an authenication cookie sets username/password from authentication cookie
    elif cookie_user != None and cookie_pass != None and st.session_state["prevent_auto_sign_in"] == False:
        st.session_state["username"] = cookie_user
        st.session_state["password"] = cookie_pass
    
    # Sets username/password for code
    username = st.session_state["username"]
    password = st.session_state["password"]

    # Logs user in
    if password != "" and username != "":
        if (username in data and password == data[username]["password"]):
            st.session_state["user"] = username
            if username == "test":  # Makes testing account correspond to Tester as a user
                st.session_state["user"] = "Tester"
            st.session_state["create_account"] = None
            st.session_state["cookies_active"] = True # Enables create cookie script at the begining of code
            st.rerun()
            
        elif username not in data:
            st.sidebar.warning(f'No username "{username}" in system.')

        elif password != data[username]["password"]:
            st.sidebar.warning("Password is incorrect.")

        else:
            st.sidebar.warning("Username or password are incorrect.")

    # Button allowing user to create an account if they don't already have one
    if st.session_state["create_account"] == False:
        for i in range(2):
            st.sidebar.write("")
        st.sidebar.subheader("Sign Up")
        st.sidebar.write("Don't have an account? Create one here:")
        if st.sidebar.button("Create account"):
            st.session_state["create_account"] = True
            st.rerun()

# Account create
if st.session_state["create_account"] == True and st.session_state["user"] == '':
    st.sidebar.subheader("Create Account")
    new_username = st.sidebar.text_input("Username:")
    new_password = st.sidebar.text_input("Password:", type="password")
    new_password2 = st.sidebar.text_input("Re-enter password:", type="password")
    st.session_state["use_cookies"] = st.sidebar.checkbox("Keep me signed in (uses cookies)", value=True)

    if new_username in data:
        st.sidebar.warning("Username already taken. Please try again.") 

    elif new_password != new_password2 and new_password != "" and new_password2 != "":
        st.sidebar.warning("Passwords do not match.")

    elif new_password != "" and new_password2 != "" and new_username != "":  
        if st.sidebar.button("Create account"):
            with open("accounts.json", 'r') as accounts_read:
                data = json.load(accounts_read)
                data.update({new_username: {'username': new_username, 'password': new_password, 'uses cookies': st.session_state["use_cookies"], "profile picture filepath": 'null', 'number of chats': 1, 'chat history': {'1':{"user_history": [],"assistant_history": []}}}})
                with open("accounts.json", 'w') as accounts_file:
                    json.dump(data, accounts_file, indent=4)

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
            st.rerun()

# Logged in display
if st.session_state["user"] != '':

    # Set user pfp
    if data[username]["profile picture filepath"] != "null":
        accounts_read = open("accounts.json", 'r')
        with open("accounts.json", 'r') as accounts_read:
            data4 = json.load(accounts_read)
            st.session_state["pfp_filepath"] = os.path.expanduser(data4[username]["profile picture filepath"])
    elif st.session_state["pfp_filepath"] != "./profile_pictures/Guest.jpg":
        st.session_state["pfp_filepath"] = None

    # Informs user of login status
    st.sidebar.subheader(f"Currently logged in as {username}.")

    # Account settings
    with st.sidebar.popover("Account Settings"):

        # User profile picture upload
        if st.session_state["user"] != "Guest":
            user_pfp_upload = st.file_uploader("Upload image for custom profile picture:", type=["png", "jpg", "jpeg"])
            st.write("(Image must be in landscape orientation \n or it will appear upside down)")
            if user_pfp_upload != None:

                # Sets file path of image
                pfps_path = os.path.expanduser("~/ProctorPal/profile_pictures")
                upload_path = os.path.join(pfps_path, user_pfp_upload.name)

                # Saves pfp to profile_pictures folder
                with open((upload_path), 'wb') as f:
                    f.write(user_pfp_upload.getvalue())

                # Updates profile picture filepath key in accounts.json
                accounts_read = open("accounts.json", 'r')
                data3 = json.load(accounts_read)
                with open("accounts.json", 'w') as accounts_write:
                    data3[st.session_state["username"]]["profile picture filepath"] = upload_path 
                    json.dump(data3, accounts_write, indent=4)
                                
                # Apply profile picture by rerunning script
                if st.button("Apply"):
                    st.rerun()
            
        # Sets admin flag for easier debuggin if correct key is entered
        if st.text_input("Beta tester keys go here:") == admin_key:
            admin = True
    
    # Button to log out
    if st.sidebar.button("Logout"):
        st.session_state["user"] = ''
        st.session_state["username"] = ''
        st.session_state["password"] = ''
        st.session_state["create_account"] = False
        st.session_state["prevent_auto_sign_in"] = True
        st.session_state["cookies_active"] = False
        st.session_state["clear"] += 1
        st.rerun()

    # Chat managmenet
    if st.session_state["user"] != "Guest":
        for i in range(2):
            st.sidebar.write('')
        st.sidebar.subheader("Chats")
        # Loads prior conversations
        with open("accounts.json", 'r') as accounts_read:
            data = json.load(accounts_read)
            st.session_state["number_of_chats"] = data[st.session_state["user"]]["number of chats"]
            chat_names = list(reversed((data[st.session_state["user"]]["chat history"].keys())))

        # Button allowing user to create new chats
        if st.sidebar.button("Create new chat"):
            if len(chat_names) < 19:
                with open("accounts.json", 'r') as accounts_read:
                    data = json.load(accounts_read)
                    data[st.session_state["user"]]["number of chats"] = len(list(chat_names)) + 1 # Updates uses number of chats flag accounts.json
                    data[st.session_state["user"]]["chat history"].update({"Chat_" + str(len(list(chat_names)) + 1): {"user_history": [],"assistant_history": []}}) # Creates new section for chat in accounts.json
                    with open("accounts.json", 'w') as accounts_write:
                        json.dump(data, accounts_write, indent=4)
                    st.rerun()
            else:
                st.sidebar.warning("You can only have up to 20 chats")
                
        # Chat selection
        selected_chat_name = st.sidebar.selectbox("Chat History", (list(chat_names)))
        st.session_state["selected_chat_name"] = selected_chat_name 
        selected_chat = chat_names.index(st.session_state["selected_chat_name"]) + 1 # Get position of the output in the list of chats

        # Creates session states for active chat
        if f"user_history{selected_chat}" not in st.session_state:
            st.session_state[f"user_history{selected_chat}"] = data[st.session_state["user"]]['chat history'][selected_chat_name]['user_history']
        if f"assistant_history{selected_chat}" not in st.session_state:
            st.session_state[f"assistant_history{selected_chat}"] = data[st.session_state["user"]]['chat history'][selected_chat_name]['assistant_history']
            
        # Prints chat
        for i in range(len(st.session_state[f"user_history{selected_chat}"])): 
            with st.chat_message("user", avatar = st.session_state["pfp_filepath"]):
                st.write(st.session_state[f"user_history{selected_chat}"][i])
            if i < len(st.session_state[f"assistant_history{selected_chat}"]):
                    with st.chat_message("assistant", avatar = "./profile_pictures/ProctorPal.png"):
                        st.write(st.session_state[f"assistant_history{selected_chat}"][i])

    # Button to restart Streamlit for easier debugging
    if admin == True: 
        if st.sidebar.button("Restart"):
            st.rerun()

    # Button allowing user to log inadaquate responses 
    if len(st.session_state[f"assistant_history{selected_chat}"]) > 0:
        for i in range(2): 
            st.sidebar.write("")
        if st.sidebar.button("Previous reponse was inadaquate"):
            with open("poor_responses.txt", "a") as p:
                p.write("\n\n" + st.session_state["username"] + ": " + st.session_state[f"user_history{selected_chat}"][-1] + "\n" + "ProctorPal: " + st.session_state[f"assistant_history{selected_chat}"][-1])
    
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
    st.session_state["pfp_filepath"] = "./profile_pictures/Guest.jpg" # Sets guest pfp
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
with st.chat_message("user", avatar = st.session_state["pfp_filepath"]):
    st.write(query)

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

# Sets ChatGPT version
if gpt_version == 3.5:
    gpt_version = "gpt-3.5-turbo-0125"
    input_cost = 0.00005
    output_cost = 0.00015
elif gpt_version == 4:
    gpt_version = "gpt-4-turbo-preview"
    input_cost = 0.001
    output_cost = 0.003

# Gives ChatGPT api input from user, results from database, and context
messages = [{"role": "system", "content": f"""You are an assistant designed to answer questions about Proctor Academy. 
             It is ok if you cannot answer a question with the data given, but DO NOT make up answers when the information was not given to you in the context.
             Include only the parts of the context that are relevant to the user question. DO NOT answer questions that aren't about Proctor."""}, 
             {"role": "user", "content": f"""Here is some potentially relevant information, but not all of it will be usefull. 
             Generally, the infromation that comes earlier will be more relevant: {str(filtered)}. Here is the user query: {str(query)}"""}]

# Stops timer for code and starts timer for generation
code_time = time.time()- code_time
gerneration_time = time.time()

# Gets ChatGPT api response
streaming_reply = oclient.chat.completions.create(
    model = gpt_version, 
    messages = messages, 
    max_tokens = gpt_tokens, 
    temperature = gpt_temperature,
    stream = True
)

# Prints ChatGPT api response
with st.chat_message("assistant", avatar = "./profile_pictures/ProctorPal.png").empty():
    reply = st.write_stream(streaming_reply) # Prints ChatGPT response

# Ends generation timer
generation_time = time.time()- gerneration_time

# Prints additional information easier debugging
if admin == True:
    st.write("Time (code):", code_time)
    st.write("Time (generation):", generation_time)
    st.write("Time (total):", code_time + generation_time)
    st.write("Model used:", gpt_version)

    # Finds and returns number of tokens in input/output
    encoding = tiktoken.encoding_for_model(gpt_version)
    tokens_input = len(encoding.encode(str(messages))) - 24
    tokens_output = len(encoding.encode(str(reply)))
    st.write("Input tokens:", tokens_input)
    st.write("Output tokens:", tokens_output)

    st.write(f"Price: {(tokens_input * input_cost) + (tokens_output * output_cost)}¢") 
    st.write("Database output:", str(filtered)) # Returns databse output
    
# Logs ChatGPT response in history
st.session_state[f"assistant_history{selected_chat}"].append(reply)

# Logs chat history in the accounts file
if username != "Guest" and  username != "test":
    user_history = st.session_state[f"user_history{selected_chat}"][-1]
    assistant_history = st.session_state[f"assistant_history{selected_chat}"][-1]

    data[username]['chat history'][selected_chat_name]['user_history'].append(user_history)
    data[username]['chat history'][selected_chat_name]['assistant_history'].append(assistant_history)

    with open("accounts.json", 'w') as accounts_file:
        json.dump(data, accounts_file, indent=4)

# Updates logs
if username != "test" and admin == False:
    with open("logs.txt", "a") as f1:
        f1.write("\n\n" + username + ": " + query + "\n" + "ProctorPal: " + reply)