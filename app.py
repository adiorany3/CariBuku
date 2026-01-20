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
- You can download, what you need, but please don't abuse this service’. Buy books to support authors.
- If you like this app, consider donating to support development. Click 'Donate' button below to see QR code.


**Disclaimer:** Ensure compliance with copyright laws.
                If robot bussy, try again later, or use alternative search link.
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
    st.session_state.show_donate = not st.session_state.show_donate

if st.session_state.show_donate:
    st.sidebar.image("aset/QRcode.jpg")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

body {
    background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 25%, #16213e 50%, #0f0f23 75%, #1a1a2e 100%);
    background-size: 400% 400%;
    animation: gradientShift 15s ease infinite;
    font-family: 'Inter', sans-serif;
    color: #ffffff;
    margin: 0;
    padding: 0;
    min-height: 100vh;
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.stApp {
    background: rgba(26, 26, 46, 0.95);
    border-radius: 20px;
    padding: 40px;
    margin: 20px auto;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 0 1px rgba(255,255,255,0.1);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.1);
    color: #ffffff;
    max-width: 1400px;
    position: relative;
    overflow: hidden;
}

.stApp::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #ffeaa7, #dda0dd);
    background-size: 400% 100%;
    animation: rainbowBorder 8s linear infinite;
}

@keyframes rainbowBorder {
    0% { background-position: 0% 0%; }
    100% { background-position: 400% 0%; }
}

.stExpander {
    border: 2px solid rgba(138, 43, 226, 0.4);
    border-radius: 15px;
    margin-bottom: 25px;
    background: linear-gradient(135deg, rgba(30, 30, 60, 0.9) 0%, rgba(40, 40, 80, 0.8) 100%);
    color: #ffffff;
    box-shadow: 0 8px 25px rgba(138, 43, 226, 0.15);
    transition: all 0.3s ease;
    overflow: hidden;
}

.stExpander:hover {
    border-color: rgba(138, 43, 226, 0.6);
    box-shadow: 0 12px 35px rgba(138, 43, 226, 0.25);
    transform: translateY(-2px);
}

.stButton>button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 16px 32px;
    text-align: center;
    text-decoration: none;
    display: block;
    width: 100%;
    font-size: 16px;
    margin: 8px 0;
    cursor: pointer;
    border-radius: 12px;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    font-weight: 500;
    letter-spacing: 0.5px;
    position: relative;
    overflow: hidden;
}

.stButton>button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    transition: left 0.5s;
}

.stButton>button:hover::before {
    left: 100%;
}

.stButton>button:hover {
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 12px 30px rgba(102, 126, 234, 0.6);
}

.alternatif-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 16px 32px;
    text-align: center;
    text-decoration: none;
    display: block;
    width: 100%;
    font-size: 16px;
    margin: 8px 0;
    cursor: pointer;
    border-radius: 12px;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    font-weight: 500;
    letter-spacing: 0.5px;
    position: relative;
    overflow: hidden;
}

.alternatif-btn:hover {
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    transform: translateY(-3px) scale(1.02);
    box-shadow: 0 12px 30px rgba(102, 126, 234, 0.6);
}

.stTextInput input {
    border-radius: 12px;
    border: 2px solid rgba(138, 43, 226, 0.4);
    padding: 16px;
    background: linear-gradient(135deg, rgba(40, 40, 70, 0.9) 0%, rgba(50, 50, 90, 0.8) 100%);
    color: #ffffff;
    font-size: 16px;
    width: 100%;
    transition: all 0.3s ease;
    box-shadow: inset 0 2px 10px rgba(0,0,0,0.1);
}

.stTextInput input:focus {
    border-color: #667eea;
    box-shadow: 0 0 20px rgba(102, 126, 234, 0.5), inset 0 2px 10px rgba(0,0,0,0.1);
    transform: scale(1.02);
}

h1 {
    color: #ffffff;
    text-align: center;
    font-size: 3.5em;
    font-weight: 700;
    text-shadow: 0 0 30px rgba(221, 160, 221, 0.8), 0 0 60px rgba(221, 160, 221, 0.4);
    margin-bottom: 40px;
    background: linear-gradient(45deg, #dda0dd, #98d8c8, #f7dc6f, #bb8fce);
    background-size: 400% 400%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: textGradient 4s ease infinite;
    letter-spacing: -1px;
}

@keyframes textGradient {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

.sidebar .sidebar-content {
    background: linear-gradient(135deg, rgba(15, 15, 35, 0.95) 0%, rgba(25, 25, 55, 0.9) 100%);
    color: #ffffff;
    border-radius: 15px;
    padding: 25px;
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255,255,255,0.1);
}

p, div, span {
    color: #ffffff;
}

.stSuccess {
    background: linear-gradient(135deg, rgba(34, 139, 34, 0.3) 0%, rgba(50, 205, 50, 0.2) 100%);
    border: 2px solid #228b22;
    border-radius: 12px;
    padding: 15px;
    margin: 15px 0;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 15px rgba(34, 139, 34, 0.2);
}

.stError {
    background: linear-gradient(135deg, rgba(220, 20, 60, 0.3) 0%, rgba(255, 69, 0, 0.2) 100%);
    border: 2px solid #dc143c;
    border-radius: 12px;
    padding: 15px;
    margin: 15px 0;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 15px rgba(220, 20, 60, 0.2);
}

.stWarning {
    background: linear-gradient(135deg, rgba(255, 165, 0, 0.3) 0%, rgba(255, 215, 0, 0.2) 100%);
    border: 2px solid #ffa500;
    border-radius: 12px;
    padding: 15px;
    margin: 15px 0;
    backdrop-filter: blur(10px);
    box-shadow: 0 4px 15px rgba(255, 165, 0, 0.2);
}

.robot-search {
    animation: robot-search 3s ease-in-out infinite;
    font-size: 1.2em;
    color: #dda0dd;
    font-weight: 600;
}

@keyframes robot-search {
    0%, 100% { transform: translateX(0) rotate(0deg); opacity: 1; }
    25% { transform: translateX(10px) rotate(2deg); opacity: 0.8; }
    50% { transform: translateY(-10px) rotate(0deg); opacity: 1; }
    75% { transform: translateX(-10px) rotate(-2deg); opacity: 0.8; }
}

.results-container {
    margin-top: 40px;
    padding: 30px;
    background: rgba(20, 20, 50, 0.8);
    border-radius: 20px;
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255,255,255,0.1);
}

.footer {
    text-align: center;
    margin-top: 60px;
    padding: 25px;
    background: linear-gradient(135deg, rgba(15, 15, 35, 0.8) 0%, rgba(25, 25, 55, 0.7) 100%);
    border-radius: 15px;
    color: #dda0dd;
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}

.footer h3 {
    margin: 0 0 10px 0;
    font-size: 1.2em;
    font-weight: 600;
}

/* Responsive design */
@media (max-width: 768px) {
    .stApp {
        padding: 20px;
        margin: 10px;
        border-radius: 15px;
    }
    
    h1 {
        font-size: 2.5em;
    }
    
    .stButton>button, .alternatif-btn {
        padding: 12px 24px;
        font-size: 14px;
    }
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(26, 26, 46, 0.5);
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #667eea, #764ba2);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #764ba2, #667eea);
}

/* Loading animation */
.stSpinner > div {
    border-color: #667eea transparent transparent transparent !important;
}

/* Progress bar styling */
.stProgress > div > div {
    background: linear-gradient(90deg, #667eea, #764ba2) !important;
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
            ]
            for name, url in mirrors:
                st.markdown(f'- <a href="{url}" target="_blank">{name}</a>', unsafe_allow_html=True)
            
            # Direct download link
            with st.spinner("Getting direct download link..."):
                direct_url = get_download_url(book['md5'])
            if direct_url:
                st.markdown(f'**Direct Download:** <a href="{direct_url}" target="_blank">Download Now</a>', unsafe_allow_html=True)
            else:
                st.write("Direct download not available")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
current_year = datetime.datetime.now().year
mirror_count = get_active_mirror_count()
total_mirrors = get_total_mirror_count()
st.markdown(f'<div class="footer">Smart Robot - Developed by Galuh Adi Insani © {current_year} | Active Mirrors: {mirror_count} / {total_mirrors}</div>', unsafe_allow_html=True)