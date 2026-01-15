import requests
from bs4 import BeautifulSoup

# List of LibGen mirrors to try
MIRRORS = [
    'https://libgen.li',
    'https://libgen.is',
    'https://libgen.rs'
]

def search_books(query, max_results=100):
    """
    Search for ebooks on LibGen using the given query.
    Returns a list of dictionaries with book details.
    """
    for mirror in MIRRORS:
        try:
            url = f"{mirror}/search.php"
            params = {
                'q': query,
                'res': max_results,
                'view': 'simple',
                'phrase': 1,
                'column': 'def'
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            table = soup.find('table', {'id': 'table'})
            if not table:
                continue
            
            rows = table.find_all('tr')[1:]  # Skip header row
            books = []
            for row in rows:
                tds = row.find_all('td')
                if len(tds) < 10:
                    continue
                
                author = tds[1].text.strip()
                title = tds[2].text.strip()
                year = tds[4].text.strip()
                
                mirror_link = tds[9].find('a')
                if mirror_link and 'md5=' in mirror_link['href']:
                    md5 = mirror_link['href'].split('md5=')[1]
                    download_url = f"{mirror}{mirror_link['href']}"
                else:
                    continue
                
                books.append({
                    'title': title,
                    'author': author,
                    'year': year,
                    'md5': md5,
                    'download_url': download_url
                })
            
            if books:
                return books
        except Exception as e:
            print(f"Failed to search on {mirror}: {e}")
            continue
    return []

def get_direct_download_url(md5):
    """
    Get the direct download URL for a book given its MD5.
    """
    for mirror in MIRRORS:
        try:
            url = f"{mirror}/ads.php"
            params = {'md5': md5}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for download links, typically starting with http:// or https://
            download_links = soup.find_all('a', href=lambda x: x and ('http://' in x or 'https://' in x) and 'download' in x.lower())
            if download_links:
                return download_links[0]['href']
            
            # Alternative: look for links in GET section
            get_section = soup.find('h2', string='GET')
            if get_section:
                link = get_section.find_next('a')
                if link:
                    return link['href']
        except Exception as e:
            print(f"Failed to get download URL from {mirror}: {e}")
            continue
    return None

def download_book(md5, filename=None):
    """
    Download a book given its MD5.
    If filename is not provided, it will be inferred from the URL.
    """
    download_url = get_direct_download_url(md5)
    if not download_url:
        print("Could not find download URL")
        return False
    
    try:
        response = requests.get(download_url, stream=True, timeout=30)
        response.raise_for_status()
        
        if not filename:
            # Infer filename from URL or Content-Disposition
            filename = download_url.split('/')[-1]
            if not filename or '.' not in filename:
                content_disp = response.headers.get('Content-Disposition')
                if content_disp and 'filename=' in content_disp:
                    filename = content_disp.split('filename=')[1].strip('"')
                else:
                    filename = f"{md5}.pdf"  # Default assumption
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded to {filename}")
        return True
    except Exception as e:
        print(f"Failed to download: {e}")
        return False

# Example usage
if __name__ == "__main__":
    query = "python programming"
    books = search_books(query)
    if books:
        print(f"Found {len(books)} books")
        for book in books[:5]:  # Show first 5
            print(f"Title: {book['title']}")
            print(f"Author: {book['author']}")
            print(f"Year: {book['year']}")
            print(f"MD5: {book['md5']}")
            print(f"Download URL: {book['download_url']}")
            print("---")
        
        # Download the first book
        if books:
            download_book(books[0]['md5'])
    else:
        print("No books found")