import streamlit as st
st.set_page_config(page_title="AIV Studios - CCTV Surveillance System", page_icon="🤖", layout="centered")
from time import sleep
from navigation import make_sidebar
import sqlite3
from streamlit_extras.app_logo import add_logo
import base64
make_sidebar()
st.markdown("""
    <style>
    /* Set text color for visibility */
    h1, h2, h3, h4, h5, h6, p, label {
        color: #FFD700; /* White text for clear visibility */
        text-align: center;
        font-family: 'Arial', sans-serif;
    }

    /* Button styling */
    .stButton>button {
        background-color: #2d3030;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #000000;
    }

    /* Make input labels and text readable */
    .stTextInput label, .stSelectbox label, .stTextArea label, .stNumberInput label {
        color: #000000; /* White labels */
    }

    /* Sidebar styling for clarity */
    .stSidebar {
        background-color: rgba(0, 0, 0, 0.6); /* Semi-transparent dark */
    }

    </style>
    """, unsafe_allow_html=True)



main_bg_ext = "face.jpg"
        
st.markdown(
        f"""
        <style>
        .stApp {{
            background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg_ext, "rb").read()).decode()});
            background-size: 100% auto
            
             
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
# hide_streamlit_style = """
#                 <style>
#                 div[data-testid="stToolbar"] {
#                 visibility: hidden;
#                 height: 0%;
#                 position: fixed;
#                 }
#                 div[data-testid="stDecoration"] {
#                 visibility: hidden;
#                 height: 0%;
#                 position: fixed;
#                 }
#                 div[data-testid="stStatusWidget"] {
#                 visibility: hidden;
#                 height: 0%;
#                 position: fixed;
#                 }
#                 #MainMenu {
#                 visibility: hidden;
#                 height: 0%;
#                 }
#                 header {
#                 visibility: hidden;
#                 height: 0%;
#                 }
#                 footer {
#                 visibility: hidden;
#                 height: 0%;
#                 }
#                 </style>
#                 """
# st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
# 
# st.title("Welcome to Diamond Corp")

# st.write("Please log in to continue (username `test`, password `test`).")

# username = st.text_input("Username")
# password = st.text_input("Password", type="password")

# if st.button("Log in", type="primary",use_container_width=True):
#     if username == "test" and password == "test":
#         st.session_state.logged_in = True
#         st.success("Logged in successfully!")
#         sleep(0.5)
#         st.switch_page("pages/page1.py")
#     else:
#         st.error("Incorrect username or password")
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = None

# if "streamdash"not in st.session_state:
#     st.session_state["streamdash"] = False


if "log_out" not in st.session_state:
    st.session_state["log_out"] = False
def create_connection():
    return sqlite3.connect("cctv_database.db", check_same_thread=False)

def check_credentials(username, password):
    with sqlite3.connect("cctv_database.db") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM user WHERE username=? AND password=?", (username, password))
        return cursor.fetchone() is not None

def show_login_page():
    st.markdown("""
        <h1 style='text-align: center; color:  #FFD700;'>🔐 CCTV Surveillance System</h1>
    """, unsafe_allow_html=True)
    
    
    st.markdown("<hr>", unsafe_allow_html=True)
    username = st.text_input("👤 Username", placeholder="Enter your username")
    password = st.text_input("🔑 Password", placeholder="Enter your password", type="password")

    if st.button("🚀 Login", use_container_width=True):
        if check_credentials(username, password):
            st.session_state.logged_in = True
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success(f"✅ Welcome, {username}!")
            st.switch_page("pages/1_streamdash.py")# ✅ FIXED PATH
            
            
            
        else:
            st.error("❌ Invalid username or password!")


if st.session_state["logged_in"]:
    st.switch_page("pages/1_streamdash.py")
    
    
    
   
else:
    show_login_page()
