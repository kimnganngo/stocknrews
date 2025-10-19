import re
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from .base import BaseScraper

class VietstockScraper(BaseScraper):
    name = "Vietstock"

    def list_article_links(self):
        links = []
        base_urls = self.cfg.get("base_urls", [])
        pag = self.cfg.get("pagination", {})
        list_sel = self.cfg.get("list_selector", "a[href]")
        allow_rx = self.cfg.get("allow_regex")
        allow_re = re.compile(allow_rx) if allow_rx else None

        def paged(url):
            if pag.get("type") == "query":
                for p in range(pag.get("start", 1), pag.get("stop", 2)):
                    yield f"{url}?{urlencode({pag.get('param','page'): p})}"
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
                    if allow_re and not allow_re.search(href):
                        continue
                    links.append(href)
        seen, out = set(), []
        for u in links:
            if u not in seen:
                out.append(u); seen.add(u)
        return out
