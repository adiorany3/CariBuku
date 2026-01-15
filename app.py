import streamlit as st
import pandas as pd
from libgen import search_books, get_download_url

st.set_page_config(
    page_title="Hidden Book Downloader",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("📖 About this app")
st.sidebar.info("""
This app allows you to search and download ebooks on Internet Archive.

- Enter a title or author to search.
- Click on results to expand and download.
- Use 'Load More' for additional results.

**Disclaimer:** Ensure compliance with copyright laws.
                If server bussy, try again later.
""")

st.sidebar.markdown("---")
st.sidebar.markdown('[Edit PDF](https://www.bentopdf.com/index.html) (opens in new tab)', unsafe_allow_html=False)

st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    color: #ffffff;
}
.stApp {
    background-color: rgba(26, 26, 46, 0.9);
    border-radius: 15px;
    padding: 30px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.1);
    color: #ffffff;
}
.stExpander {
    border: 1px solid rgba(138, 43, 226, 0.3);
    border-radius: 10px;
    margin-bottom: 20px;
    background-color: rgba(30, 30, 60, 0.8);
    color: #ffffff;
    box-shadow: 0 4px 15px rgba(138, 43, 226, 0.1);
}
.stButton>button {
    background: linear-gradient(45deg, #6a5acd, #483d8b);
    color: white;
    border: none;
    padding: 14px 28px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    font-size: 16px;
    margin: 6px 3px;
    cursor: pointer;
    border-radius: 10px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(106, 90, 205, 0.3);
}
.stButton>button:hover {
    background: linear-gradient(45deg, #483d8b, #6a5acd);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(106, 90, 205, 0.4);
}
.stTextInput input {
    border-radius: 8px;
    border: 1px solid rgba(138, 43, 226, 0.3);
    padding: 12px;
    background-color: rgba(40, 40, 70, 0.8);
    color: #ffffff;
    font-size: 16px;
}
.stTextInput input:focus {
    border-color: #6a5acd;
    box-shadow: 0 0 10px rgba(106, 90, 205, 0.5);
}
h1 {
    color: #dda0dd;
    text-align: center;
    font-size: 3em;
    font-weight: bold;
    text-shadow: 0 0 20px rgba(221, 160, 221, 0.5);
    margin-bottom: 30px;
}
.sidebar .sidebar-content {
    background-color: rgba(15, 15, 35, 0.9);
    color: #ffffff;
    border-radius: 10px;
    padding: 20px;
}
p, div, span {
    color: #ffffff;
}
.stSuccess {
    background-color: rgba(34, 139, 34, 0.2);
    border: 1px solid #228b22;
}
.stError {
    background-color: rgba(220, 20, 60, 0.2);
    border: 1px solid #dc143c;
}
.robot-search {
    animation: robot-search 2s infinite;
    font-size: 1em;
    color: #dda0dd;
}
@keyframes robot-search {
    0% { transform: translateX(0); }
    25% { transform: translateX(5px); }
    50% { transform: translateY(-5px); }
    75% { transform: translateX(-5px); }
    100% { transform: translateX(0); }
}
</style>
""", unsafe_allow_html=True)

# Search functionality
query = st.text_input("Enter book title or author:")

if 'results' not in st.session_state:
    st.session_state.results = []
if 'page' not in st.session_state:
    st.session_state.page = 1
if 'current_query' not in st.session_state:
    st.session_state.current_query = ""

def perform_search():
    placeholder = st.empty()
    placeholder.markdown(f'<div style="display: flex; justify-content: center; align-items: center; height: 100px;"><div class="robot-search">🤖 Smart robot deep thinking, please wait, we will search at page {st.session_state.page}...</div></div>', unsafe_allow_html=True)
    new_results = search_books(st.session_state.current_query, max_results=20, page=st.session_state.page)
    placeholder.empty()
    if new_results:
        st.session_state.results.extend(new_results)
        st.success(f"Loaded {len(new_results)} more results (total: {len(st.session_state.results)})")
    else:
        st.error("No more results found.")

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("Search", key="search_btn"):
        if query:
            st.session_state.results = []
            st.session_state.page = 1
            st.session_state.current_query = query
            perform_search()
        else:
            st.error("Please enter a search query.")

with col2:
    if st.button("Clear History", key="clear_history_btn"):
        st.session_state.results = []
        st.session_state.page = 1
        st.session_state.current_query = ""
        st.success("History cleared. Display reset to initial state.")

with col3:
    if st.button("Load More", key="load_more_btn") and st.session_state.current_query:
        st.session_state.page += 1
        perform_search()

if st.session_state.results:
    st.write(f"Total results: {len(st.session_state.results)}")
    for i, book in enumerate(st.session_state.results):
        with st.expander(f"{book['title']} by {book['author']} ({book['year']}) - {book['size']} {book['extension']}"):
            st.write(f"**Publisher:** {book['publisher']}")
            st.write(f"**Language:** {book['language']}")
            st.write(f"**Pages:** {book['pages']}")
            download_url = get_download_url(book['md5'])
            if download_url:
                st.markdown(f'<a href="{download_url}" target="_blank">Download (opens in new tab)</a>', unsafe_allow_html=True)
            else:
                st.error("Download URL not available")

st.markdown("---")
st.markdown('<p style="text-align: center; color: #dda0dd;">Smart Robot - Developed by Galuh Adi Insani</p>', unsafe_allow_html=True)