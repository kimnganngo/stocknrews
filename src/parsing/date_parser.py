import re
from datetime import datetime
from dateutil import parser, tz
from bs4 import BeautifulSoup

TZ = tz.gettz("Asia/Bangkok")

def _first_meta_datetime(soup: BeautifulSoup, selectors):
    for sel in selectors:
        if "::" in sel:
            css, attr = sel.split("::", 1)
        else:
            css, attr = sel, None
        for node in soup.select(css):
            if attr:
                val = node.get(attr)
            else:
                val = node.get_text(" ", strip=True)
            if not val:
                continue
            try:
                dt = parser.parse(val)
                return dt
            except Exception:
                continue
    return None

def _date_from_url(url: str, url_rx: str):
    if not url_rx:
        return None
    m = re.search(url_rx, url)
    if not m:
        return None
    y, mth, d = map(int, m.groups())
    return datetime(y, mth, d, 8, 0)

def parse_article_datetime(html: str, url: str, cfg: dict):
    """Return (datetime_tz, display_str) or (None, "Không rõ")."""
    soup = BeautifulSoup(html or "", "lxml")
    dt = _first_meta_datetime(soup, cfg.get("date_selectors", []))
    if dt is None:
        dt = _date_from_url(url or "", cfg.get("url_date_regex"))
    if dt is None:
        return None, "Không rõ"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=TZ)
    dt = dt.astimezone(TZ)
    return dt, dt.strftime("%d/%m/%Y %H:%M")
