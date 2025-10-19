import random
import time
from dataclasses import dataclass
from typing import List, Optional, Dict

import requests
from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/120.0",
]

def _sleep_throttle():
    time.sleep(random.uniform(0.2, 0.6))

@dataclass
class Article:
    url: str
    title: str
    html: str
    content: str

class BaseScraper:
    name: str = "Base"

    def __init__(self, cfg: Dict):
        self.cfg = cfg
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": random.choice(USER_AGENTS)})
        self.date_configs = {
            "date_selectors": cfg.get("date_selectors", []),
            "url_date_regex": cfg.get("url_date_regex"),
        }

    def _get(self, url: str) -> str:
        for attempt in range(3):
            try:
                _sleep_throttle()
                r = self.session.get(url, timeout=15)
                if r.status_code == 200:
                    return r.text
            except requests.RequestException:
                pass
        raise RuntimeError(f"HTTP error for {url}")

    def list_article_links(self) -> List[str]:
        raise NotImplementedError

    def fetch_article(self, url: str) -> Article:
        html = self._get(url)
        soup = BeautifulSoup(html, "lxml")
        title = soup.find("title").get_text(strip=True) if soup.title else url
        content = ""
        for sel in self.cfg.get("content_selectors", []):
            for node in soup.select(sel):
                content = content + "\n" + node.get_text(" ", strip=True)
            if content:
                break
        return Article(url=url, title=title, html=html, content=content.strip())
