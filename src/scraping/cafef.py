import re
from urllib.parse import urlencode, urlparse
from bs4 import BeautifulSoup
from .base import BaseScraper

class CafeFScraper(BaseScraper):
    name = "CafeF"

    def list_article_links(self):
        links = []
        base_urls = self.cfg.get("base_urls", [])
        pag = self.cfg.get("pagination", {})
        allow = self.cfg.get("allow_pattern")
        list_sel = self.cfg.get("list_selector", "a[href]")

        def paged(url):
            if pag.get("type") == "query":
                for p in range(pag.get("start", 1), pag.get("stop", 2)):
                    yield f"{url}?{urlencode({pag.get('param','p'): p})}"
            else:
                yield url

        for base in base_urls:
            for url in paged(base):
                html = self._get(url)
                soup = BeautifulSoup(html, "lxml")
                for a in soup.select(list_sel):
                    href = a.get("href", "")
                    if not href.startswith("http"):
                        continue
                    if allow and allow not in href:
                        continue
                    links.append(href)
        seen = set(); out = []
        for u in links:
            if u not in seen:
                out.append(u); seen.add(u)
        return out
