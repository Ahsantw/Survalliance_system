import streamlit as st
st.set_page_config(page_title="Remove Person", page_icon="❌", layout="wide")
import sqlite3
import re
import os
import re
import cv2
import sqlite3
import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import time
import zmq
# from client_add import zmqConnect1
import base64
from navigation import make_sidebar
# Page Configuration

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

from streamlit_extras.stylable_container import stylable_container

# Create buttons with st.button

# hide_sidebar_css = """
# <style>
#     section[data-testid="stSidebar"] {
#         display: none;
#     }
# </style>
# """
# st.markdown(hide_sidebar_css, unsafe_allow_html=True)

main_bg_ext = "face.jpg"
        
st.markdown(
        f"""
        <style>
        .stApp {{
            background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg_ext, "rb").read()).decode()});
            background-size: cover
            
            

            
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
# st.image("aivlogotrans.png", width=550, use_container_width=False)


# if st.button("⬅️ Go Back"):
#     st.session_state["logged_in"] = True
#     st.switch_page("pages/1_streamdash.py")
    
st.markdown(
    """
    <style>
    .title {
        color: #FFD700 !important; /* Change title color */
        text-align: center;
        font-size: 36px;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Display the Custom Title
st.markdown('<h1 class="title">Remove Person Information</h1>', unsafe_allow_html=True)

# st.title("Remove Person Information")

# def clear_fields():
# def clear_fields():
#     st.switch_page("pages/addperson.py")
#     # st.rerun()

make_sidebar()    

# Initialize session state for input fields
if "id" not in st.session_state:
    st.session_state.id = ""


# Database Connection
def get_db_connection():
    return sqlite3.connect("cctv_database.db")

# Function to add a person to the database
def rem_person(id):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM employee WHERE uniqueid = ?", (id,))
        connection.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"Failed to delete person: {e}")
        return False
    finally:
        connection.close()

# Input Validation Functions



# Form for Input Fields and Submission
with st.form("person_form", clear_on_submit=True):
    id = st.text_input("Unique ID:", placeholder="Please Enter Unique ID e.g (2-2-2025)")    
    # Submit Button
    with stylable_container(
    "black",
    css_styles="""
    button {
        background-color: #2d3030;
        color: white;

    }

    """,

    ):
        submitted = st.form_submit_button("❌ Remove Person")
folder_path = "images"
# Validation and Submission Logic
if submitted:

    if rem_person(id):

        st.success("✅ Person ID remove Successfully!")

        file_path = os.path.join(folder_path, f"{id}.jpg")
        if os.path.exists(file_path):
            os.remove(file_path)
            st.success("✅ Person Image removed Successfully!")
            os.system("python database.py")
            st.success(f"✅ Database updated at: {file_path}")

        
        # send1 = zmqConnect1("tcp://localhost:5555")

        # with st.spinner("🚀 Sending image..."):
        #     captured_image = np.zeros((112, 112, 3), dtype=np.uint8)
        #     check=0
        #     response = send1.imshow(captured_image,id,check)
        # if response:
        #     st.success("✅ Person Details remove Successfully!")
        #     st.success(response.decode())

        else:
            st.error("❌ No Picture Exit.")
    else:
        st.error("❌ ID not exit.")




    




