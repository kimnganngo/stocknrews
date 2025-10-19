import streamlit as st

@st.cache_data(show_spinner=False, ttl=900)
def cache_html(url: str, html: str):
    return html
