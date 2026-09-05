import streamlit as st
st.set_page_config(page_title="Add Person", page_icon="➕", layout="wide")
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

# from client_add import zmqConnect1
import base64
# Page Configuration
from navigation import make_sidebar





st.markdown("""
    <style>
    /* Set text color for visibility */
    h1, h2, h3, h4, h5, h6, p, label {
        color: #FFD700 ; /* White text for clear visibility */
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
st.markdown('<h1 class="title">Add New Person Information</h1>', unsafe_allow_html=True)



make_sidebar()
# def clear_fields():
def clear_fields():
    st.switch_page("pages/addperson.py")
    # st.rerun()
     

# Initialize session state for input fields
if "id" not in st.session_state:
    st.session_state.id = ""
if "name" not in st.session_state:
    st.session_state.name = ""
if "fname" not in st.session_state:
    st.session_state.fname = ""
if "position" not in st.session_state:
    st.session_state.position = ""
if "dob" not in st.session_state:
    st.session_state.dob = ""
if "contact" not in st.session_state:
    st.session_state.contact = ""
if "email" not in st.session_state:
    st.session_state.email = ""

# Database Connection
def get_db_connection():
    return sqlite3.connect("cctv_database.db")

# Function to add a person to the database
def add_person(id, name, fname, position, dob, contact, email):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
        INSERT INTO employee (uniqueid, name, fname, position, dob, phone, email)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id, name, fname, position, dob, contact, email))
        connection.commit()
        return True
    except sqlite3.Error as e:
        st.error(f"Failed to add person: {e}")
        return False
    finally:
        connection.close()

# Input Validation Functions
def validate_name(name):
    if not name.strip():
        return "Name cannot be empty."
    if not re.match(r"^[A-Za-z\s]+$", name):
        return "Name should contain only letters and spaces."
    return None

def validate_phone(phone):
    if not re.match(r"^\+?[0-9\- ]+$", phone):
        return "Invalid phone number. Only digits, '+', '-', and spaces are allowed."
    return None

def validate_email(email):
    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
        return "Invalid email address."
    return None

def validate_dob(dob):
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", dob):
        return "Invalid date of birth. Use YYYY-MM-DD format."
    return None

def validate_fname(fname):
    if not fname.strip():
        return "Father/Guardian name cannot be empty."
    if not re.match(r"^[A-Za-z\s]+$", fname):
        return "Father/Guardian name should contain only letters and spaces."
    return None

def validate_position(position):
    if not position.strip():
        return "Position cannot be empty."
    return None
if "cam" not in st.session_state:
    st.session_state["cam"] = False

    st.session_state["captured_image"] = None


# Form for Input Fields and Submission
with st.form("person_form", clear_on_submit=True):
    id = st.text_input("Unique ID:", placeholder="Please Enter Unique ID e.g (2-2-2025)")
    name = st.text_input("Name:", placeholder="Please Enter Name")
    fname = st.text_input("Father/Guardian Name:", placeholder="Please Enter Father/Guardian Name")
    position = st.text_input("Position:", placeholder="Please Enter Position")
    dob = st.text_input("Date of Birth (YYYY-MM-DD)")
    contact = st.text_input("Contact Number:", placeholder="Please Enter Contact Number")
    email = st.text_input("Email:", placeholder="Please Enter Email")

    submitted = st.form_submit_button("➕ Add Person")

# Validation and Submission Logic
if submitted:
    # Validate all fields
    errors = {
        "name": validate_name(name),
        "fname": validate_fname(fname),
        "position": validate_position(position),
        "dob": validate_dob(dob),
        "contact": validate_phone(contact),
        "email": validate_email(email),
    }

    # Check if there are any validation errors
    if any(errors.values()):
        for field, error in errors.items():
            if error:
                st.error(f"{field.capitalize()}: {error}")
    else:
        # If no errors, add the person to the database
        if add_person(id, name, fname, position, dob, contact, email):
            st.success("✅ Person Details Added Successfully!")


col0,col1, col2= st.columns(3)
with col0: cam_button = st.button("📷 webCam")
with col1: capture_button = st.button("📷 Capture")
with col2: save_button = st.button("💾 Save")

if cam_button:
    st.session_state["cam"] = not st.session_state["cam"]   # Toggle the state

frame_placeholder = st.empty()

if st.session_state["cam"]:
    # st.session_state["logged_in"] = True
    cap = cv2.VideoCapture(0)
    
    

    if not cap.isOpened():
        st.error("❌ Unable to open video file!")
        
    
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            st.warning("📹 Video Ended!")
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        orig_height, orig_width, _ = frame_rgb.shape

        # Define crop size as a percentage of the original size
        crop_width = int(orig_width * 0.8)  # 80% of original width
        crop_height = int(orig_height * 0.5)  # 60% of original height

        # Compute center coordinates
        center_x, center_y = orig_width // 2, orig_height // 2

        # Compute cropping box
        x_start = max(center_x - crop_width // 2, 0)
        x_end = min(center_x + crop_width // 2, orig_width)
        y_start = max(center_y - crop_height // 2, 0)
        y_end = min(center_y + crop_height // 2, orig_height)

        # Crop the image
        frame_cropped = frame_rgb[y_start:y_end, x_start:x_end]

        # **Reduce the canvas size** (only slightly larger than cropped image)
        canvas_width = int(crop_width * 1.1)  # 10% larger
        canvas_height = int(crop_height * 1.1)  # 10% larger

        # Create a blank white canvas
        canvas = np.ones((canvas_height, canvas_width, 3), dtype=np.uint8) * 255

        # Compute offsets to center the cropped frame on the canvas
        x_offset = (canvas.shape[1] - frame_cropped.shape[1]) // 2
        y_offset = (canvas.shape[0] - frame_cropped.shape[0]) // 2

        # Place the cropped frame in the middle of the **smaller canvas**
        canvas[y_offset:y_offset + frame_cropped.shape[0], x_offset:x_offset + frame_cropped.shape[1]] = frame_cropped


        # Display the **cropped & centered image** in Streamlit
        frame_placeholder.image(canvas, caption="Live Video Feed", use_container_width=False)

        if capture_button:
            st.session_state["captured_image"] = canvas.copy()
            st.success("✅ Image Captured!")
            # frame_placeholder = st.empty()
            st.session_state["cam"]=False
            cap.release()
            st.rerun()  
            
            break


            
    cap.release()
else:
    if st.session_state["captured_image"] is not None:
    # frame_placeholder = st.empty()
        captured_image=st.session_state["captured_image"]
        # cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        frame_placeholder.image(captured_image, caption="Captured Image", use_container_width=False)
    else:
        frame_placeholder = st.empty()
SAVE_DIR = "images"
os.makedirs(SAVE_DIR, exist_ok=True)   
if save_button and st.session_state["captured_image"] is not None:
    image_path = os.path.join(SAVE_DIR, f"{id}.jpg")
    savepic=cv2.cvtColor(captured_image, cv2.COLOR_BGR2RGB)
    cv2.imwrite(image_path, savepic)
    st.success(f"✅ Image saved at: {image_path}")
    os.system("python database.py")
    st.success(f"✅ Database updated at: {image_path}")

# send1 = zmqConnect1("tcp://localhost:5555")
# if send_button and captured_image is not None:
#     with st.spinner("🚀 Sending image..."):
#         check=1
#         response = send1.imshow(captured_image,id,check)
#     if response:
#         st.write(response)

#     else:
#         st.error("❌ No Response from Server.")

