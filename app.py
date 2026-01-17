import streamlit as st
import pandas as pd
from libgen import search_books, get_download_url, get_active_mirror_count, get_total_mirror_count
import datetime
import random
import streamlit.components.v1 as components

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = []
if 'page' not in st.session_state:
    st.session_state.page = 1
if 'current_query' not in st.session_state:
    st.session_state.current_query = ""
if 'show_donate' not in st.session_state:
    st.session_state.show_donate = False
if 'input_query' not in st.session_state:
    st.session_state.input_query = ""

st.set_page_config(
    page_title="Hidden Book Downloader",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("📖 About this app")
st.sidebar.info("""
This app allows you to search and download ebooks on Internet Archive.

- Enter a title or author to search. Robot will search for matching books.
- Click on results to expand and download. Enjoy reading!
- Use 'Load More' for additional results.

**Disclaimer:** Ensure compliance with copyright laws.
                If robot bussy, try again later.
""")

st.sidebar.markdown("---")
st.sidebar.markdown('[Edit PDF](https://www.bentopdf.com/index.html) (opens in new tab)', unsafe_allow_html=False)
st.sidebar.markdown('[Cek Server](https://open-slum.pages.dev/) (opens in new tab)', unsafe_allow_html=False)

quotes = [
    '> "A reader lives a thousand lives before he dies. The man who never reads lives only one." – George R.R. Martin',
    '> "The more that you read, the more things you will know. The more that you learn, the more places you’ll go." – Dr. Seuss',
    '> "Books are a uniquely portable magic." – Stephen King',
    '> "Reading is to the mind what exercise is to the body." – Joseph Addison',
    '> "There is no friend as loyal as a book." – Ernest Hemingway',
    '> "A book is a dream that you hold in your hand." – Neil Gaiman',
    '> "Reading gives us someplace to go when we have to stay where we are." – Mason Cooley',
    '> "The reading of all good books is like conversation with the finest men of past centuries." – René Descartes',
    '> "Books are mirrors: you only see in them what you already have inside you." – Carlos Ruiz Zafón',
    '> "I have always imagined that Paradise will be a kind of library." – Jorge Luis Borges',
    '> "Books are the quietest and most constant of friends; they are the most accessible and wisest of counselors, and the most patient of teachers." – Charles W. Eliot'
]
st.sidebar.markdown(random.choice(quotes))

if st.sidebar.button("Donate"):
    st.session_state.show_donate = True

if st.session_state.show_donate:
    st.sidebar.image("aset/QRcode.jpg")

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
    max-width: 1200px;
    margin: 0 auto;
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
    display: block;
    width: 100%;
    font-size: 16px;
    margin: 6px 0;
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
.alternatif-btn {
    background: linear-gradient(45deg, #6a5acd, #483d8b);
    color: white;
    border: none;
    padding: 14px 28px;
    text-align: center;
    text-decoration: none;
    display: block;
    width: 100%;
    font-size: 16px;
    margin: 6px 0;
    cursor: pointer;
    border-radius: 10px;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(106, 90, 205, 0.3);
}
.alternatif-btn:hover {
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
    width: 100%;
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
    border-radius: 5px;
    padding: 10px;
    margin: 10px 0;
}
.stError {
    background-color: rgba(220, 20, 60, 0.2);
    border: 1px solid #dc143c;
    border-radius: 5px;
    padding: 10px;
    margin: 10px 0;
}
.stWarning {
    background-color: rgba(255, 165, 0, 0.2);
    border: 1px solid #ffa500;
    border-radius: 5px;
    padding: 10px;
    margin: 10px 0;
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
.results-container {
    margin-top: 30px;
}
.footer {
    text-align: center;
    margin-top: 50px;
    padding: 20px;
    background-color: rgba(15, 15, 35, 0.5);
    border-radius: 10px;
    color: #dda0dd;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 style="text-align: center; color: #dda0dd;">🤖 Robot is ready to deep searching</h1>', unsafe_allow_html=True)

# Search functionality
query = st.text_input("Enter book title or author here:", value=st.session_state.input_query, key="query_input")

# Update session state when user types
if query != st.session_state.input_query:
    st.session_state.input_query = query

# Constants for messages
SEARCH_LOADING_MESSAGE = "🤖 Smart robot is deep searching, please wait... (Page {page})"
RESULTS_SUCCESS_MESSAGE = "Loaded {count} more results (total: {total})"
NO_RESULTS_MESSAGE = "No more results found, try different keywords, or maybe try the alternative search."
SEARCH_ERROR_MESSAGE = "An error occurred while searching. Please try again."

def perform_search():
    try:
        with st.spinner(SEARCH_LOADING_MESSAGE.format(page=st.session_state.page)):
            new_results = search_books(st.session_state.current_query, max_results=20, page=st.session_state.page)
        if new_results:
            st.session_state.results.extend(new_results)
            st.success(RESULTS_SUCCESS_MESSAGE.format(count=len(new_results), total=len(st.session_state.results)))
        else:
            st.warning(NO_RESULTS_MESSAGE)
            components.html("""
            <button class="alternatif-btn" onclick="window.open('https://carifile.streamlit.app/', '_blank')">Click Here to Try Alternative Search</button>
            """)
    except Exception as e:
        st.error(SEARCH_ERROR_MESSAGE)
        # Optional: log the error for debugging
        print(f"Search error: {e}")

col1, col2, col3 = st.columns([1, 1, 1])

st.markdown('<div style="margin-top: 20px;">', unsafe_allow_html=True)
with col1:
    if st.button("Search", key="search_btn"):
        if query:
            st.session_state.results = []
            st.session_state.page = 1
            st.session_state.current_query = query
            st.session_state.input_query = query  # Keep the input field value
            perform_search()
        else:
            st.error("Please enter a search query.")

with col2:
    if st.button("Clear History", key="clear_history_btn"):
        st.session_state.results = []
        st.session_state.page = 1
        st.session_state.current_query = ""
        st.session_state.input_query = ""
        st.success("History cleared. Display reset to initial state.")

with col3:
    col3a, col3b = st.columns(2)
    with col3a:
        if st.button("Load More", key="load_more_btn") and st.session_state.current_query:
            st.session_state.page += 1
            perform_search()
    with col3b:
        components.html("""
        <button class="alternatif-btn" onclick="window.open('https://carifile.streamlit.app/', '_blank')">Alternatif Search</button>
        """)
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.results:
    st.markdown('<div class="results-container">', unsafe_allow_html=True)
    st.write(f"Robot founds: {len(st.session_state.results)}")
    for i, book in enumerate(st.session_state.results):
        with st.expander(f"{book['title']} by {book['author']} ({book['year']}) - {book['size']} {book['extension']}"):
            st.write(f"**Publisher:** {book['publisher']}")
            st.write(f"**Language:** {book['language']}")
            st.write(f"**Pages:** {book['pages']}")
            st.write("**Mirrors:**")
            mirrors = [
                ("LibGen", f"https://libgen.is/ads.php?md5={book['md5']}"),
                ("LibGen.rs", f"https://libgen.rs/ads.php?md5={book['md5']}"),
                ("Randombook", f"https://randombook.org/book/{book['md5']}"),
                ("Anna's Archive", f"https://en.annas-archive.org/md5/{book['md5']}"),
                ("LibGen.pw", f"https://libgen.pw/book/{book['md5']}"),
                ("BookSC", f"https://booksc.org/s/{book['md5']}"),
            ]
            for name, url in mirrors:
                st.markdown(f'- <a href="{url}" target="_blank">{name}</a>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
current_year = datetime.datetime.now().year
mirror_count = get_active_mirror_count()
total_mirrors = get_total_mirror_count()
st.markdown(f'<div class="footer">Smart Robot - Developed by Galuh Adi Insani © {current_year} | Active Mirrors: {mirror_count} / {total_mirrors}</div>', unsafe_allow_html=True)