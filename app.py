import streamlit as st
import pandas as pd
from libgen import search_books, get_active_mirror_count, get_total_mirror_count, get_download_url
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


# About section at the very top
st.sidebar.markdown("""
<div style='margin-bottom: 0.5em;'>
<h2 style='margin-bottom:0.2em;font-size:1.3em;'>📖 About</h2>
<div style='font-size:1em;'>
🔍 Search & download ebooks instantly.<br>
1. Masukkan judul/penulis, klik <b>Search</b>.<br>
2. Klik hasil untuk download.<br>
3. Gunakan <b>Load More</b> untuk hasil tambahan.<br>
<br>💡 Dukung penulis dengan membeli buku asli.<br>
<span style='color:#e17055;'>⚠️ Disclaimer: Patuhi hukum hak cipta. Jika robot sibuk, coba lagi atau gunakan alternatif.</span>
</div>
</div>
""", unsafe_allow_html=True)

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
    st.session_state.show_donate = not st.session_state.show_donate

if st.session_state.show_donate:
    st.sidebar.image("aset/QRcode.jpg")

st.markdown("""
<style>
body {
    background: linear-gradient(135deg, #f0f2f6 0%, #e3e9f7 100%);
    font-family: 'Segoe UI', Arial, sans-serif;
}
.stApp {
    max-width: 1100px;
    margin: 0 auto;
    padding: 20px;
}
h1, .main-title {
    color: #4a3aff;
    text-align: center;
    font-weight: 700;
    margin-bottom: 0.5em;
    letter-spacing: 1px;
}
.stButton>button {
    background: linear-gradient(90deg, #4a3aff 0%, #00c6fb 100%);
    color: white;
    border: none;
    padding: 12px 28px;
    border-radius: 8px;
    font-size: 1.1em;
    font-weight: 600;
    box-shadow: 0 2px 8px rgba(76, 58, 255, 0.08);
    transition: background 0.2s;
}
.stButton>button:hover {
    background: linear-gradient(90deg, #00c6fb 0%, #4a3aff 100%);
}
.stTextInput input {
    padding: 12px;
    border-radius: 8px;
    border: 1.5px solid #4a3aff33;
    font-size: 1.1em;
}
.stExpander {
    border: 1.5px solid #4a3aff33;
    border-radius: 10px;
    margin-bottom: 18px;
    background: #fff;
    box-shadow: 0 2px 8px rgba(76, 58, 255, 0.04);
}
.results-container {
    display: flex;
    flex-wrap: wrap;
    gap: 18px;
    justify-content: center;
    margin-top: 18px;
}
.book-card {
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 2px 12px rgba(76, 58, 255, 0.07);
    padding: 22px 28px 18px 28px;
    min-width: 320px;
    max-width: 370px;
    flex: 1 1 320px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    border: 1.5px solid #4a3aff22;
}
.book-title {
    font-size: 1.18em;
    font-weight: 700;
    color: #4a3aff;
    margin-bottom: 2px;
}
.book-meta {
    font-size: 0.98em;
    color: #444;
    margin-bottom: 2px;
}
.book-download {
    margin-top: 10px;
    font-weight: 600;
    color: #00b894;
}
.footer {
    margin-top: 32px;
    color: #888;
    font-size: 0.98em;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)


st.markdown('<div class="main-title"><span style="font-size:2.2em;">🤖 Cari Buku</span><br><span style="font-size:1.1em;font-weight:400;color:#555;">Search & Download Free Ebooks Instantly</span></div>', unsafe_allow_html=True)

# Search functionality
query = st.text_input("Enter book title or author here:", value=st.session_state.input_query, key="query_input")

# Constants for messages
SEARCH_LOADING_MESSAGE = "🤖 Smart robot is deep searching, please wait... (Page {page})"
RESULTS_SUCCESS_MESSAGE = "Loaded {count} more results (total: {total})"
NO_RESULTS_MESSAGE = "No more results found, try different keywords, or maybe try the alternative search."
SEARCH_ERROR_MESSAGE = "An error occurred while searching. Please try again."

def perform_search():
    try:
        with st.spinner(SEARCH_LOADING_MESSAGE.format(page=st.session_state.page)):
            new_results = search_books(st.session_state.current_query, max_results=25, page=st.session_state.page)
        # Hindari duplikasi berdasarkan md5
        existing_md5 = set(book.get('md5') for book in st.session_state.results)
        filtered_results = [book for book in new_results if book.get('md5') not in existing_md5]
        if filtered_results:
            st.session_state.results.extend(filtered_results)
            st.success(RESULTS_SUCCESS_MESSAGE.format(count=len(filtered_results), total=len(st.session_state.results)))
        else:
            st.warning(NO_RESULTS_MESSAGE)
            st.markdown('<a href="https://carifile.streamlit.app/" target="_blank" style="display: inline-block; padding: 16px 32px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 12px; text-decoration: none; font-weight: 500;">Click Here to Try Alternative Search</a>', unsafe_allow_html=True)
    except Exception as e:
        st.error(SEARCH_ERROR_MESSAGE)
        print(f"Search error: {e}")

st.markdown('<div style="margin-top: 20px;">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

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
    if st.button("Load More", key="load_more_btn") and st.session_state.current_query:
        st.session_state.page += 1
        perform_search()

with col4:
    st.markdown('<a href="https://carifile.streamlit.app/" target="_blank" class="alternatif-btn" style="display: inline-block; padding: 16px 32px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 12px; text-decoration: none; font-weight: 500;">Alternatif Search</a>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.results:
    st.markdown('<div class="results-container">', unsafe_allow_html=True)
    for i, book in enumerate(st.session_state.results):
        with st.container():
            st.markdown(f'''
            <div class="book-card">
                <div class="book-title">📚 {book.get('title', '-') }</div>
                <div class="book-meta"><b>Author:</b> {book.get('author', '-') } &nbsp;|&nbsp; <b>Year:</b> {book.get('year', '-') } &nbsp;|&nbsp; <b>Lang:</b> {book.get('language', '-') }</div>
                <div class="book-meta"><b>Publisher:</b> {book.get('publisher', '-') } &nbsp;|&nbsp; <b>Pages:</b> {book.get('pages', '-') } &nbsp;|&nbsp; <b>Size:</b> {book.get('size', '-') } {book.get('extension', '-') }</div>
            ''', unsafe_allow_html=True)
            with st.spinner("Getting direct download link... Please wait..."):
                direct_url = get_download_url(book['md5']) if 'md5' in book else None
            if direct_url:
                st.markdown(f'<div class="book-download">🔗 <a href="{direct_url}" target="_blank">Download Now</a></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="book-download" style="color:#e17055;">Direct download not available</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
current_year = datetime.datetime.now().year
mirror_count = get_active_mirror_count()
total_mirrors = get_total_mirror_count()
st.markdown(f'<div class="footer">Smart Robot - Developed by Galuh Adi Insani © {current_year} | Active Mirrors: {mirror_count} / {total_mirrors}</div>', unsafe_allow_html=True)