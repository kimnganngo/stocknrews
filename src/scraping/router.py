from typing import Dict
from .cafef import CafeFScraper
from .vietstock import VietstockScraper

class ScraperRouter:
    def __init__(self, cfg: Dict):
        self.cfg = cfg

    def get_scraper_by_name(self, name: str):
        for s in self.cfg.get("sources", []):
            if s.get("name") == name:
                if name == "CafeF":
                    return CafeFScraper(s)
                if name == "Vietstock":
                    return VietstockScraper(s)
        raise ValueError(f"Unknown source {name}")
