import os
import re
import requests
import string
from urllib.parse import urljoin, urlparse, quote
import logging

# List of file extensions to download
FILE_EXTENSIONS = [
    ".svg", ".jpg", ".jpeg", ".png", ".gif", ".ico", ".css", ".js", ".html",
    ".php", ".json", ".ttf", ".otf", ".woff2", ".woff", ".eot", ".mp4", ".ogg"
]

# List of file extensions to scan for links
SCAN_EXTENSIONS = [".css", ".js", ".html", ".php", ".json"]

def create_tor_session():
    session = requests.Session()
    session.proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    }
    return session

def fetch_url(url, session):
    url = quote(url, safe=string.printable)
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    return session.get(url, headers=headers)

def get_local_filename(url, local_path):
    parsed_url = urlparse(url)
    path = parsed_url.path.lstrip('/')
    
    if not path or not os.path.splitext(path)[1]:  # Check if there's no path or no file extension
        path = os.path.join(path, 'index.html')  # Use 'index.html' for the root path or add it
    
    local_filename = os.path.join(local_path, path)
    
    return local_filename

def download_file(session, url, local_filename):
    try:
        os.makedirs(os.path.dirname(local_filename), exist_ok=True)
        
        with fetch_url(url, session) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)

        logging.info(f"Downloaded: {url} -> {local_filename}")
        return True
    except Exception as e:
        logging.error(f"Error downloading {url}: {e}")
        return False

def validate_url(url):
    parsed_url = urlparse(url)
    path_without_extensions = parsed_url.path
    for extension in FILE_EXTENSIONS:
        path_without_extensions = re.sub(re.escape(extension) + r'$', '', path_without_extensions)
    
    invalid_chars = set(string.punctuation.replace('/', '').replace('-', '').replace('.', '').replace('_', '').replace('@', ''))
    if any(char in invalid_chars for char in path_without_extensions):
        return False
    
    return True

def extract_links(content, base_url, add_to_queue_func):
    urls = []
    pattern = r'([^=\"\'(\s]+)' + str('(' + '|'.join(FILE_EXTENSIONS) + ')').replace(".", "\.") + r'([^\"\'\)>\s]*)'
    links = re.findall(pattern, content, re.IGNORECASE)
    for link in links:
        url = ''.join(link)
        if url:
            url = url.strip(' "\'')
            if validate_url(url):
                absolute_url = urljoin(base_url, url)
                add_to_queue_func(absolute_url)
                urls.append(absolute_url)
    return urls

def update_links(content, local_path, urls):
    url_map = {url: '/' + os.path.relpath(get_local_filename(url, local_path), start=local_path) for url in urls}
 
    pattern = re.compile('|'.join(re.escape(url) for url in url_map.keys()))
    
    def replace_match(match):
        return url_map[match.group(0)]
    
    content = pattern.sub(replace_match, content)
    
    return content

def process_html_file(local_filename, current_url, local_path, add_to_queue_func):
    try:
        with open(local_filename, 'r', encoding='utf-8') as f:
            content = f.read()

        urls = extract_links(content, current_url, add_to_queue_func)
        updated_content = update_links(content, local_path, urls)
        with open(local_filename, 'w', encoding='utf-8') as f:
            f.write(updated_content)
    except Exception as e:
        logging.error(f"Error processing {local_filename}: {e}")

def add_to_queue(link, to_visit, visited):
    if link not in to_visit and link not in visited:
        to_visit.add(link)

def download_site(url, local_path):
    visited = set()
    to_visit = {url}
    session = create_tor_session()
    
    while to_visit:
        current_url = to_visit.pop()
        visited.add(current_url)

        local_filename = get_local_filename(current_url, local_path)

        if os.path.exists(local_filename):
            logging.info(f"Skipping {current_url} as {local_filename} already exists.")
            continue

        if download_file(session, current_url, local_filename):
            if any(local_filename.endswith(ext) for ext in SCAN_EXTENSIONS):
                process_html_file(local_filename, current_url, local_path, lambda link: add_to_queue(link, to_visit, visited))
