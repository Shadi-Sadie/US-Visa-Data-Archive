import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


HEADERS = {"User-Agent": "Mozilla/5.0"}
DOWNLOAD_DIR = "data/raw"


def scrape_pdfs(base_url, required_keywords):
    response = requests.get(base_url, headers=HEADERS, timeout=10)
    response.raise_for_status()

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

    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()

    with open(path, "wb") as f:
        f.write(response.content)

    return path
