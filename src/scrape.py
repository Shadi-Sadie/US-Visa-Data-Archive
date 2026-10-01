import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


HEADERS = {"User-Agent": "Mozilla/5.0"}
DOWNLOAD_DIR = "data/raw"
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 10


def _get_with_retries(url, timeout):
    last_exc = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            last_exc = e
            if attempt < MAX_RETRIES:
                wait = RETRY_BACKOFF_SECONDS * attempt
                print(f"Request to {url} failed ({e}); retrying in {wait}s...")
                time.sleep(wait)
    raise last_exc


def scrape_pdfs(base_url, required_keywords):
    response = _get_with_retries(base_url, timeout=10)

    soup = BeautifulSoup(response.text, "html.parser")
    pdfs = []

    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        text = a.get_text(strip=True).lower()
        combined = href + " " + text

        if href.endswith(".pdf") and any(k.lower() in combined for k in required_keywords):
            pdfs.append(urljoin(base_url, a["href"]))

    return pdfs


def download_pdf(url):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    filename = url.split("/")[-1]
    path = os.path.join(DOWNLOAD_DIR, filename)

    if os.path.exists(path):
        return path

    response = _get_with_retries(url, timeout=30)

    with open(path, "wb") as f:
        f.write(response.content)

    return path
