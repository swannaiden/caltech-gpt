import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time
import PyPDF2
from io import BytesIO

REQUEST_DELAY = 5  # Delay between requests in seconds

def is_valid(url, domain):
    parsed_url = urlparse(url)
    return bool(parsed_url.netloc) and parsed_url.netloc.endswith(domain)

def is_allowed_file_type(url):
    allowed_file_types = ['.html', '.pdf', '.txt']
    parsed_url = urlparse(url)
    file_extension = os.path.splitext(parsed_url.path)[1]

    return file_extension in allowed_file_types or not file_extension

def is_bot_protected(url):
    blacklist = ['captcha', 'robot', 'bot', 'spider', 'antibot', 'antispam', 'antivirus', 'security', 'security', 'firewall', 'protection', 'proteger', 'protección', 'protegido', 'protegida', 'protegidos', 'protegidas', 'proteger','email-protection']
    if( any(word in url.lower() for word in blacklist) ):
        print("AntiBot detected: " + url)
        return True
    else:
        return False

def get_all_links(url, domain):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch links from {url}: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    links = [a.get('href') for a in soup.find_all('a', href=True)]
    valid_links = [urljoin(url, link) for link in links if is_valid(urljoin(url, link), domain)]
    return valid_links

def extract_pdf_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch content from {url}: {e}")
        return ''

    with BytesIO(response.content) as pdf_data:
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_data)
            text = ''
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except PyPDF2.errors.PdfReadError as e:
            print(f"Failed to read PDF content from {url}: {e}")
            return ''

def save_text(url, output_file):
    if url.lower().endswith('.pdf'):
        text = extract_pdf_text(url)
    else:
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to fetch content from {url}: {e}")
            return

        soup = BeautifulSoup(response.content, "html.parser")
        text = '\n'.join(soup.stripped_strings)

    with open(output_file, 'a', encoding='utf-8') as f:
        if '\uFFFD' not in text:
            f.write(f'\n------- {url} -------\n')
            f.write(text + '\n')

def save_visited_url(url, visited_urls_file):
    with open(visited_urls_file, 'a', encoding='utf-8') as f:
        f.write(url + '\n')

def save_to_visit_list(to_visit, to_visit_file):
    with open(to_visit_file, 'w', encoding='utf-8') as f:
        for url in to_visit:
            f.write(url + '\n')

def load_visited_urls(visited_urls_file):
    if not os.path.exists(visited_urls_file):
        return set()
    with open(visited_urls_file, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f.readlines())
    
def load_to_visit_list(to_visit_file):
    if not os.path.exists(to_visit_file):
        return []

    with open(to_visit_file, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines()]

def crawl_domain(domain, start_url=None, output_file='output.txt', visited_urls_file='visited_urls.txt', to_visit_file='to_visit.txt'):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    os.makedirs(os.path.dirname(visited_urls_file), exist_ok=True)
    os.makedirs(os.path.dirname(to_visit_file), exist_ok=True)

    visited_links = load_visited_urls(visited_urls_file)
    to_visit = load_to_visit_list(to_visit_file)

    if start_url and is_valid(start_url, domain) and start_url not in visited_links:
        to_visit.insert(0, start_url)

    if not to_visit:
        to_visit.append(f'https://{domain}')

    while to_visit:
        current_link = to_visit.pop(0)

        if current_link not in visited_links and is_allowed_file_type(current_link) and not is_bot_protected(current_link):
            visited_links.add(current_link)
            print(f'Crawling {current_link}')
            save_text(current_link, output_file)
            save_visited_url(current_link, visited_urls_file)

            new_links = get_all_links(current_link, domain)
            to_visit.extend(new_links)

            save_to_visit_list(to_visit, to_visit_file)

            time.sleep(REQUEST_DELAY)


if __name__ == "__main__":
    domain = 'caltech.edu'  # Replace with the desired domain
    optional_start_url = None #'https://www.example.com/some-page'  # Replace with an optional starting URL within the domain, or set to None
    crawl_domain(domain, optional_start_url, 'output/output2.txt', 'output/visited_urls2.txt', 'output/to_visit2.txt')
    # save_text('https://hr.caltech.edu/documents/2732/blue_cross_claim_form.pdf', 'output/output3.txt')
    
