import streamlit as st
from time import sleep
from streamlit.runtime.scriptrunner import get_script_run_ctx
from streamlit.source_util import get_pages
from streamlit_extras.app_logo import add_logo

def get_current_page_name():
    ctx = get_script_run_ctx()
    if ctx is None:
        raise RuntimeError("Couldn't get script context")

    pages = get_pages("")

    return pages[ctx.page_script_hash]["page_name"]

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
def make_sidebar():
    st.sidebar.image("aivlogotrans.png")
    st.sidebar.image("Neura-Face-rem.png")
    
    with st.sidebar:
        st.title("💎 Neura Face")
        
        st.write("")
        st.write("")

        if st.session_state.get("logged_in", False):
            # st.page_link("pages/page1.py", label="Secret Company Stuff", icon="🔒")
            # st.page_link("pages/page2.py", label="More Secret Stuff", icon="🕵️")
            st.page_link("pages/1_streamdash.py", label="Dashboard", icon="📊")
            st.page_link("pages/2_addperson.py", label="Add Person", icon="➕")
            st.page_link("pages/3_removeperson.py", label="Remove Person", icon="❌")
            st.page_link("pages/4_Searching.py", label="Search Person", icon="🔍")
            add_logo("cctv_logo.png", height=320)

            st.write("")
            st.write("")

            if st.button("Log out"):
                logout()

        elif get_current_page_name() != "streamlit_app":
            # If anyone tries to access a secret page without being logged in,
            # redirect them to the login page
            st.switch_page("streamlit_app.py")
            add_logo("cctv_logo.png", height=320)


def logout():
    st.session_state.logged_in = False
    st.info("Logged out successfully!")
    sleep(0.5)
    st.switch_page("streamlit_app.py")
