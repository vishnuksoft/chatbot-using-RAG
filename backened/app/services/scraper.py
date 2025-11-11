import trafilatura
import requests

def scrape_url(url: str) -> str:
    # you can add headers / timeouts here
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    downloaded = trafilatura.extract(resp.text, url=url, include_comments=False, include_tables=False)
    return downloaded or ""
