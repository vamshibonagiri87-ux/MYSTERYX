import streamlit as st

st.set_page_config(page_title="MYSTERYX — The Room That Thinks",page_icon="🕵️",layout="wide",initial_sidebar_state="collapsed")

pages = [
    st.Page("pages/0_MYSTERYX.py", title="MYSTERYX", icon="🔎", default=True),
    st.Page("pages/1_Create_Mystery.py", title="Create a Case", icon="🗂️"),
    st.Page("pages/2_Investigation_Room.py", title="Investigation Room", icon="🕵️"),
    st.Page("pages/3_Accusation.py", title="Make Your Guess", icon="📌"),
    st.Page("pages/4_Results.py", title="Case Results", icon="🏆"),
    st.Page("pages/5_Solved_Cases.py", title="Solved Cases", icon="📚"),
]
st.navigation(pages, position="sidebar").run()
