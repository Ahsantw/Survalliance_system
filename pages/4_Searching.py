import streamlit as st

st.set_page_config(
    page_title="CCTV Monitoring Dashboard",
    layout="wide", page_icon=":bar_chart:",
 
)
import sqlite3
import pandas as pd
import re  
import streamlit as st
import sqlite3
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import time
import zmq
from navigation import make_sidebar
import base64
from time import sleep  

from streamlit_extras.app_logo import add_logo
make_sidebar()
global count 
# from streamlit_autorefresh import st_autorefresh
# st_autorefresh(interval=5000, key="data_refresh")
# Function to fetch data from SQLite
# def fetch_data(cctv):
#     with sqlite3.connect("cctv_database.db") as conn:
#         query = f"SELECT id, person_id, name, date_time,camera_id FROM {cctv}"
#         df = pd.read_sql(query, conn)
#         df.rename(columns={"id": "Serial Number", "person_id": "Person ID", "name": "Name", "date_time": "Date/Time","camera_id":"Camera_ID"}, inplace=True)
#         return df


SAVE_DIR = "cards"
os.makedirs(SAVE_DIR, exist_ok=True)


if "selected_cards" not in st.session_state:
    st.session_state.selected_cards = {}

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


# st.set_page_config(page_title="Dashboard", page_icon="🤖", layout="wide")
# if st.session_state["logged_in"]:
#     st.session_state["logged_in"] = False
# print(st.session_state["logged_in"])

# hide_pages([Page("../login.py"),])

# st.set_page_config(layout="wide")
# st.markdown("""
#     <style>
#     body {
#         background-color: #0B0C10;
#         color: white;
#     }
#     .reportview-container {
#         background: #1F2833;
#     }
#     .sidebar .sidebar-content {
#         background: #0B0C10;
#     }
#     .css-1d391kg {
#         color: white;
#     }
#     </style>
# """, unsafe_allow_html=True)

# st.sidebar.image("cctv_logo.png", width=250)
# st.sidebar.title("Navigation")

# def add_logo():
#     st.markdown(
#         """
#         <style>
#             [data-testid="stSidebar"] {
#                 background-image: cctv_logo.png;
#                 background-repeat: no-repeat;
#                 padding-top: 120px;
#                 background-position: 20px 20px;
#             }
#             [data-testid="stSidebar"]::before {
#                 content: "My Company Name";
#                 margin-left: 20px;
#                 margin-top: 20px;
#                 font-size: 30px;
#                 position: relative;
#                 top: 100px;
#             }
#         </style>
#         """,
#         unsafe_allow_html=True,
#     )
# add_logo()

# add_logo("cctv_logo.png", height=320)
# hide_sidebar_css = """
# <style>
#     section[data-testid="stSidebar"] {
#         display: none;
#     }
# </style>
# """
# st.markdown(hide_sidebar_css, unsafe_allow_html=True)

# logout_button = st.button("🚪 Logout")
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
# st.image("aivlogotrans.png", width=450, use_container_width=False)

st.markdown("<h1 style='text-align: center; color: #66FCF1;'>CCTV Surveillance Dashboard</h1>", unsafe_allow_html=True)
# page = st.sidebar.radio("Go to", ["Entry Logs", "Exit Logs"])
# st.sidebar.multipage_menu("streamdash.py")
def fetch_data(cctv):
    with sqlite3.connect("cctv_database.db") as conn:
        query = f"SELECT person_id, name, date_time, camera_id FROM {cctv} ORDER BY date_time DESC"
        df = pd.read_sql(query, conn)

        if df.empty:
            return df  # Return an empty DataFrame if no records found

        # Reset index to make "Serial Number" start from 1
        df.reset_index(drop=True, inplace=True)
        df.index += 1  # Start index from 1

        df.rename(columns={"person_id": "Person ID", 
                           "name": "Name", "date_time": "Date/Time", "camera_id": "Camera_ID"}, inplace=True)

        df.insert(0, "Serial Number", df.index)

        return df
  
@st.cache_data(show_spinner=False)
def split_frame(input_df, rows):
    df = [input_df.loc[i : i + rows - 1, :] for i in range(0, len(input_df), rows)]
    return df


def search_patient(option,search):
    search_type = option
    search_query = search


    # if not search_query and search_type != "All Patients":
    #     st.error("Please enter search query!")
    #     return
    # if search_query == "-":
    #     messagebox.showerror("Error", "Please enter search query!")
    #     return

    # if search_type == "Person_ID":
    #     if not re.match(r"^\d+(-\d+)?$", search_query):
    #         st.error("Error", "MR Number must be numeric and can contain hyphens (e.g., 3-122024)!")
    #         return

    # Contact Validation (must be numeric)
    if search_type == "Person_ID" and search !="":
        if not search_query.isdigit():
            st.error("Person ID must be numeric!")
            return

    # Doctor Search (flexible matching, remove periods and spaces

    # Name Validation (alphabetic only)
    elif search_type == "Name"and search !="":
        if not re.match("^[a-zA-Z ]+$", search_query):
            st.error(f"{search_type} must contain only letters!")
            return
    elif search_type == "Date"and search !="":
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", search_query):
            st.error("Date must be in YYYY-MM-DD format!")
            return
    elif search_type == "Camera_ID" and search !="":
        if not search_query.isdigit():
            st.error("Camera ID must be numeric!")
            return
        

    # connection = sqlite3.connect(databasepath)
    # cursor = connection.cursor()
    with sqlite3.connect("cctv_database.db") as conn:
        if search_type == "Person_ID":
            query = "SELECT person_id, name, date_time, camera_id FROM cctv WHERE person_id LIKE ? ORDER BY date_time DESC"
            # query = "SELECT * FROM cctv WHERE person_id LIKE ?"
            df = pd.read_sql(query, conn, params=('%' + search_query + '%',))
            if not df.empty:  # Corrected check for an empty DataFrame
                df.reset_index(drop=True, inplace=True)
                df.index += 1  # Start index from 1
                df.rename(columns={"person_id": "Person ID", 
                                "name": "Name", "date_time": "Date/Time", "camera_id": "Camera_ID"}, inplace=True)
                df.insert(0, "Serial Number", df.index)
                return df
            else:
                st.error("No Record Found")  # Ensure this runs before returning None
                return
        
        elif search_type == "Name":
            query = "SELECT person_id, name, date_time, camera_id FROM cctv WHERE name LIKE ? ORDER BY date_time DESC"
            df = pd.read_sql(query, conn, params=('%' + search_query + '%',))

            if not df.empty:
                # Reset index to make "Serial Number" start from 1
                df.reset_index(drop=True, inplace=True)
                df.index += 1  # Start index from 1

                # Rename columns
                df.rename(columns={"person_id": "Person ID", "name": "Name", 
                                "date_time": "Date/Time", "camera_id": "Camera_ID"}, inplace=True)

                # Add "Serial Number" as a new column
                df.insert(0, "Serial Number", df.index)

                return df
            else:
                st.error("No Record Found")  # Ensure this runs before returning None
                return
            
        elif search_type == "Camera_ID":
            query = "SELECT person_id, name, date_time, camera_id FROM cctv WHERE camera_id LIKE ? ORDER BY date_time DESC"
            # query = "SELECT * FROM cctv WHERE camera_id LIKE ?"
            df = pd.read_sql(query, conn, params=('%' + search_query + '%',))
            if not df.empty:  # Corrected check for an empty DataFrame
                df.reset_index(drop=True, inplace=True)
                df.index += 1  # Start index from 1
                df.rename(columns={"person_id": "Person ID", 
                                "name": "Name", "date_time": "Date/Time", "camera_id": "Camera_ID"}, inplace=True)
                df.insert(0, "Serial Number", df.index)

                return df
            else:
                st.error("No Record Found")  # Ensure this runs before returning None
                return
            
        elif search_type == "Date":
            query = "SELECT person_id, name, date_time, camera_id FROM cctv WHERE date_time LIKE ? ORDER BY date_time DESC"
            # query = "SELECT * FROM cctv WHERE date_time LIKE ?"
            df = pd.read_sql(query, conn, params=('%' + search_query + '%',))
            if not df.empty:  # Corrected check for an empty DataFrame
                df.reset_index(drop=True, inplace=True)
                df.index += 1  # Start index from 1
                df.rename(columns={"person_id": "Person ID", 
                                "name": "Name", "date_time": "Date/Time", "camera_id": "Camera_ID"}, inplace=True)
                df.insert(0, "Serial Number", df.index)
                return df
            else:
                st.error("No Record Found")  # Ensure this runs before returning None
                return 


        # elif search_type == "All Patients":
        #     cursor.execute("SELECT * FROM patients")
        else:
            st.error("Invalid search type selected!")
            return

        # results = cursor.fetchall()
        # #print(type(results))
        # connection.close()

# Streamlit UI
# st.title("CCTV Entry/Exit Records")

def create_employee_card(details):
    img_width, img_height = 600, 450
    background_color = "black"
    text_color = "white"
    header_color = "#003366"
    header_text_color = "white"
    border_color = "#003366"

    img = Image.new("RGB", (img_width, img_height), background_color)
    draw = ImageDraw.Draw(img)

    try:
        header_font = ImageFont.truetype("arial.ttf", 26)
        font = ImageFont.truetype("arial.ttf", 22)
    except:
        header_font = ImageFont.load_default()
        font = ImageFont.load_default()

    draw.rectangle([(0, 0), (img_width, 60)], fill=header_color)
    header_text = "Person Details Card"
    draw.text((img_width // 6, 15), header_text, fill=header_text_color, font=header_font)

    text_lines = [
        f"Person Details",
        f"Unique ID: {details[1]}",
        f"Name: {details[2]}",
        f"Father Name: {details[3]}",
        f"Position: {details[4]}",
        f"DOB: {details[5]}",
        f"Contact: {details[6]}",
        f"Email: {details[7]}"
    ]

    y_position = 90
    for line in text_lines:
        draw.text((50, y_position), line, fill=text_color, font=font)
        y_position += 40

    draw.rectangle([(5, 5), (img_width - 5, img_height - 5)], outline=border_color, width=5)
    card_path = os.path.join(SAVE_DIR, f"employee_card_{details[1]}.jpg")
    img.save(card_path)
    return card_path
        
    



  

    # st.write("You selected:", option)
    # table_placeholder = st.empty()
    # table_placeholder.table(fetch_data("cctv"))
placeselect=st.empty()
search_placeholder=st.empty()
pagination = st.empty()
placecolumn=st.empty()


option = placeselect.selectbox(
"How would you like to be search?",
("Person_ID", "Name", "Date","Camera_ID"),
index=None,
placeholder="Select searching method..."
)


    

# def searching(option,batch_size,current_page):



    


    
df_main=fetch_data("cctv")
# df_main = pd.DataFrame({
#     "Serial Number": range(1, 101),  # Simulated data (1 to 100)
#     "Person ID": [f"ID_{i}" for i in range(1, 101)],
#     "Name": [f"Person_{i}" for i in range(1, 101)],
#     "Date/Time": pd.date_range("2025-03-12", periods=100, freq="H"),
#     "Camera_ID": [1, 2] * 50
# })


bottom_menu = placecolumn.columns((4, 1, 1))
with bottom_menu[2]:
    batch_size = st.selectbox("Page Size", options=[25, 50, 100])
    
with bottom_menu[1]:
    if int(len(df_main) / batch_size)> 0:
        if int(len(df_main) % batch_size)==0:
            total_pages= int(len(df_main) / batch_size)
        else:
            total_pages= int(len(df_main) / batch_size)+1


    else:
        total_pages=1

    # total_pages = (
    #     int(len(df_main) / batch_size)+1   else 1
    # )
    current_page = st.number_input(
        "Page", min_value=1, max_value=total_pages, step=1
        
    )
    
with bottom_menu[0]:
    st.markdown(f"Page **{current_page}** of **{total_pages}** ")


def mpg_change():
    edited_rows: dict = session_state.mpg['edited_rows']
    session_state.selected_row_index = next(iter(edited_rows))
    session_state.df = session_state.df.assign(selected=False)
    update_dict = {idx: values for idx, values in edited_rows.items()}
    session_state.df.update(pd.DataFrame.from_dict(update_dict, orient='index'))
    
    
if "selected_row" not in st.session_state:
    st.session_state.selected_row = None
if "selected_employee_ids" not in st.session_state:
    st.session_state.selected_employee_ids = set()

if "employee_card_paths" not in st.session_state:
    st.session_state.employee_card_paths = {}

DATABASE_PATH = "cctv_database.db"

def fetch_employee_details(employee_id):
    """Fetch employee details from SQLite database."""
    with sqlite3.connect(DATABASE_PATH) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM employee WHERE uniqueid = ?", (employee_id,))
        result = cursor.fetchone()
    return result

if not df_main.empty:
    df_main.insert(0, 'Select', False)
    pages = split_frame(df_main, batch_size)
    # print(type(pages))
    # styled_df = pages.style.set_properties(**{
    #     "background-color": "white", 
    #     "color": "black", 
    #     "border-color": "black", 
    #     'text-align': 'center'
    # })
    
    edited_df=pagination.data_editor(data=pages[current_page - 1],num_rows="dynamic", use_container_width=True,hide_index=True,
                                     column_config={"Select": st.column_config.CheckboxColumn("Select")},key="unique_key",)
    selected_indices = edited_df[edited_df["Select"]].index.tolist()

    # if selected_indices:
    #     selected_index = selected_indices[0]  # Get first selected row index
    #     if st.session_state.selected_row is None or st.session_state.selected_row != selected_index:
    #         # Update session state with the new selected row
    #         df_main["Select"] = False  # Deselect all
    #         df_main.loc[selected_index, "Select"] = True  # Select only the new row
    #         st.session_state.selected_row = selected_index
    #         st.rerun()  # Rerun to update UI
    
    # selected_rows = edited_df[edited_df["Select"]].drop(columns=["Select"])
    # if not selected_rows.empty:
    #     first_values = list(set(selected_rows.iloc[:, 1]))
    # place=st.empty()
    # placeselected=st.empty()
    # place.write("Selected Row(s):")
    # print(type(selected_rows))
    # placeselected.write(selected_rows)
    selected_ids = set(edited_df.loc[selected_indices, "Person ID"])

    # Update session state to track selections
    st.session_state.selected_employee_ids = selected_ids

    # Display selected employee details
    place = st.empty()
    placeselected = st.empty()
    place.write("Selected Row(s):")
    placeselected.write(edited_df[edited_df["Select"]])

    # Generate cards for each selected employee
    st.subheader("Generated Employee Cards")

    if st.session_state.selected_employee_ids:
        cols = st.columns(len(st.session_state.selected_employee_ids))
        
        for idx, emp_id in enumerate(st.session_state.selected_employee_ids):
            emp_details = fetch_employee_details(emp_id)  # Fetch from database
            if emp_details:
                if emp_id not in st.session_state.employee_card_paths:
                    # Generate and store card if not already created
                    card_path = create_employee_card(emp_details)
                    st.session_state.employee_card_paths[emp_id] = card_path
                
                with cols[idx]:
                    st.image(st.session_state.employee_card_paths[emp_id], caption=f"Employee ID: {emp_id}")
            else:
                st.session_state.employee_card_paths.clear()  # Clear cards when no employee is selected
# st.write(styled_df.to_html(), unsafe_allow_html=True)
# edited_df = st.dataframe(
#     df_main,
#     num_rows="dynamic",
#     use_container_width=True,
#     )   

if option:
    
    if option=="Date":
        search = search_placeholder.text_input("🔍 Search", placeholder=f"Please Enter {option} in format YYYY-MM-DD")
        
    else:
        search = search_placeholder.text_input("🔍 Search", placeholder=f"Please Enter {option}")
        


    df_main=search_patient(option,search)
    if not df_main.empty:
        if df_main is not None and not df_main.empty and search !="":
            df_main.insert(0, 'Select', False)
            pages = split_frame(df_main, batch_size)
            edited_df=pagination.data_editor(data=pages[current_page - 1],num_rows="dynamic", use_container_width=True,hide_index=True,
                                            column_config={"Select": st.column_config.CheckboxColumn("Select")},key="unique",)
            selected_indices = edited_df[edited_df["Select"]].index.tolist()

            if selected_indices:
                selected_index = selected_indices[0]  # Get first selected row index
                if st.session_state.selected_row is None or st.session_state.selected_row != selected_index:
                    # Update session state with the new selected row
                    df_main["Select"] = False  # Deselect all
                    df_main.loc[selected_index, "Select"] = True  # Select only the new row
                    st.session_state.selected_row = selected_index
                    st.rerun()  # Rerun to update UI
            
            selected_rows = edited_df[edited_df["Select"]].drop(columns=["Select"])
            if not selected_rows.empty:
                first_values = list(set(selected_rows.iloc[:, 1]))
            
            place.write("Selected Row(s):")
            placeselected.write(selected_rows)
        elif search!="":
            st.error("No Record Found")
            # while option:
            # searching(option,batch_size,current_page)
            # option,key=selectoption()

# placeselected=st.empty()



# if logout_button:
#     st.session_state["logged_in"] = False
#     st.session_state["username"] = None
#     st.switch_page("streamlit_app.py")  # ✅ Redirect to login page



# Select Entry or Exit
# option = st.selectbox("Select Record Type", ["Entry", "Exit"])

# # Display the selected records
# if option == "Entry":
#     st.table(fetch_data("entry_table"))
# elif option == "Exit":
#     st.table(fetch_data("exit_table"))