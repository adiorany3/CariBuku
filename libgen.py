import requests
from bs4 import BeautifulSoup
import time
import re
import concurrent.futures
import threading

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

MIRRORS = [
    "https://libgen.bz/",
    "https://libgen.li/",
    "https://libgen.la/",
    "https://libgen.vg/",
    "https://libgen.gl/",
    "https://libgen.is/",
    "https://libgen.rs/",
    "https://libgen.st/",
    "https://libgen.rocks/",
    "https://libgen.fun/",
    "https://libgen.me/",
    "https://libgen.org/",
    "https://libgen.io/",
    "https://libgen.pm/",
    "https://libgen.gs/",
    "https://libgen.lc/",
    "https://libgen.vc/",
    "https://libgen.cx/",
    "https://libgen.tf/",
    "https://libgen.gg/",
    "https://libgen.hk/",
    "https://libgen.onl/",
    "https://libgen.tw/",
    "https://libgen.cc/",
    "https://libgen.nl/",
]

ACTIVE_MIRRORS = []
MIRROR_CHECK_INTERVAL = 300  # 5 minutes

def check_mirror(mirror):
    try:
        response = requests.head(mirror, headers=HEADERS, timeout=5)
        return mirror if response.status_code == 200 else None
    except:
        return None

def update_active_mirrors():
    global ACTIVE_MIRRORS
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(check_mirror, MIRRORS))
    ACTIVE_MIRRORS = [r for r in results if r]
    print(f"Updated active mirrors: {len(ACTIVE_MIRRORS)} active out of {len(MIRRORS)}")

def background_mirror_check():
    while True:
        update_active_mirrors()
        time.sleep(MIRROR_CHECK_INTERVAL)

# Start background thread for mirror checking
mirror_thread = threading.Thread(target=background_mirror_check, daemon=True)
mirror_thread.start()

def search_books(query, max_results=10, page=1):
    mirrors_to_use = ACTIVE_MIRRORS if ACTIVE_MIRRORS else MIRRORS
    for mirror in mirrors_to_use:
        try:
            url = f"{mirror}index.php?req={query}&lg_topic=libgen&open=0&view=simple&res=25&phrase=1&column=def&curtab=f&order=&ordermode=desc&filesuns=all&page={page}"
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml')
            table = soup.find('table', id='tablelibgen')
            if not table:
                continue
            rows = table.find_all('tr')[1:]  # Skip header
            books = []
            for row in rows[:max_results]:
                cols = row.find_all('td')
                if len(cols) != 9:
                    continue
                # Clean title: parse the td content
                td_soup = BeautifulSoup(str(cols[0]), 'lxml')
                # Remove badges and ISBN
                for tag in td_soup.find_all(['span', 'font', 'i']):
                    tag.decompose()
                title = td_soup.get_text().strip()
                # Remove extra spaces
                title = ' '.join(title.split())
                author = cols[1].text.strip()
                publisher = cols[2].text.strip()
                year = cols[3].text.strip()
                language = cols[4].text.strip()
                pages = cols[5].text.strip()
                size = cols[6].text.strip()
                extension = cols[7].text.strip()
                md5_link = cols[8].find('a')
                if not md5_link or 'md5=' not in md5_link['href']:
                    continue
                md5 = md5_link['href'].split('md5=')[1]
                book = {
                    'title': title,
                    'author': author,
                    'publisher': publisher,
                    'year': year,
                    'language': language,
                    'pages': pages,
                    'size': size,
                    'extension': extension,
                    'md5': md5,
                }
                books.append(book)
            if books:
                return books
        except Exception as e:
            print(f"Error with mirror {mirror}: {e}")
            continue
    return []

def get_download_url(md5):
    mirrors_to_use = ACTIVE_MIRRORS if ACTIVE_MIRRORS else MIRRORS
    for mirror in mirrors_to_use:
        try:
            url = f"{mirror}ads.php?md5={md5}"
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'lxml')
            h2 = soup.find('h2', string='GET')
            if h2:
                link = h2.find_parent('a')
                if link and link['href']:
                    if link['href'].startswith('http'):
                        full_url = link['href']
                    else:
                        full_url = mirror.rstrip('/') + '/' + link['href'].lstrip('/')
                    return full_url
        except Exception as e:
            print(f"Error getting download for {md5} on {mirror}: {e}")
            continue
    return None

def download_book(md5, filename=None):
    url = get_download_url(md5)
    if not url:
        return False, "Could not get download URL"
    try:
        response = requests.get(url, headers=HEADERS, timeout=30, stream=True)
        response.raise_for_status()
        if not filename:
            content_disp = response.headers.get('Content-Disposition', '')
            if 'filename=' in content_disp:
                filename = content_disp.split('filename=')[-1].strip('"')
            else:
                filename = f"{md5}.{response.headers.get('Content-Type', '').split('/')[-1] or 'pdf'}"
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        return True, filename
    except Exception as e:
        return False, str(e)